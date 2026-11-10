"""Read-only, fixed-host GitHub retrieval with bounded pagination."""
import json
import re
import time
from urllib.parse import urlsplit

import httpx

from .schemas import Issue, Repository


class GitHubError(RuntimeError):
    pass


def parse_repository(value: str) -> str:
    if not isinstance(value, str) or len(value) > 250:
        raise GitHubError("Enter a public GitHub repository URL or owner/repo.")
    value = value.strip()
    if value.startswith("https://"):
        parsed = urlsplit(value)
        if parsed.netloc != "github.com" or parsed.query or parsed.fragment:
            raise GitHubError("Use https://github.com/owner/repo without query parameters.")
        value = parsed.path.strip("/")
    value = value.removesuffix(".git")
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9_.-]{1,100}", value):
        raise GitHubError("Enter a public GitHub repository URL or owner/repo.")
    if value.split("/")[1] in {".", ".."}:
        raise GitHubError("Invalid repository name.")
    return value


class GitHubClient:
    def __init__(self, token="", *, transport=None, sleep=time.sleep):
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.client = httpx.Client(base_url="https://api.github.com", headers=headers,
                                   timeout=20, follow_redirects=False, transport=transport)
        self.sleep = sleep

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.client.close()

    def _get(self, path, params=None):
        for attempt in range(3):
            try:
                response = self.client.get(path, params=params)
            except httpx.TransportError:
                if attempt < 2:
                    self.sleep(2 ** attempt)
                    continue
                raise GitHubError("GitHub could not be reached. Please try again.") from None
            if response.status_code in {403, 429}:
                raise GitHubError("GitHub access is restricted or rate limited. Check your token or try later.")
            if response.status_code == 404:
                raise GitHubError("Repository not found or private. Enter an accessible public repository.")
            if response.status_code >= 500 and attempt < 2:
                self.sleep(2 ** attempt)
                continue
            if response.status_code != 200:
                raise GitHubError("GitHub could not return this repository. Check the URL and access token.")
            if len(response.content) > 8_000_000:
                raise GitHubError("GitHub response exceeded the safe size limit.")
            try:
                return response.json()
            except ValueError:
                raise GitHubError("GitHub returned an invalid response.") from None

    def fetch(self, repository: str, limit: int = 20):
        name = parse_repository(repository)
        if limit not in {10, 20, 30, 50}:
            raise GitHubError("Issue limit must be 10, 20, 30, or 50.")
        try:
            data = self._get(f"/repos/{name}")
            if data.get("private"):
                raise GitHubError("Only public repositories are supported.")
            repo = Repository(full_name=name, description=(data.get("description") or "")[:2000],
                              stars=data["stargazers_count"], open_items=data["open_issues_count"],
                              url=f"https://github.com/{name}")
            issues = []
            warnings = []
            # GitHub's issues endpoint includes pull requests. Never follow arbitrary Link URLs.
            for page in range(1, 11):
                rows = self._get(f"/repos/{name}/issues", {"state": "open", "sort": "created",
                                  "direction": "desc", "per_page": 100, "page": page})
                if not isinstance(rows, list):
                    raise GitHubError("GitHub returned an invalid issues response.")
                for row in rows:
                    if "pull_request" in row:
                        continue
                    body = row.get("body") or ""
                    issues.append(Issue.model_validate_json(json.dumps({
                        "number": row["number"], "title": row["title"][:500], "body": body[:12000],
                        "labels": [label["name"][:100] for label in row.get("labels", [])[:50]],
                        "created_at": row["created_at"], "updated_at": row["updated_at"],
                        "comments": row["comments"], "url": f"https://github.com/{name}/issues/{row['number']}",
                        "truncated": len(body) > 12000 or len(row["title"]) > 500,
                    })))
                    if len(issues) == limit:
                        break
                if len(issues) == limit or len(rows) < 100:
                    break
            else:
                warnings.append("Pagination capped at 1,000 open items; the issue sample may be smaller than requested.")
            if any(issue.truncated for issue in issues):
                warnings.append("Long issue text was truncated to the analysis input limit.")
            return repo, issues, warnings
        except (KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, GitHubError):
                raise
            raise GitHubError("GitHub returned unexpected repository data.") from None
