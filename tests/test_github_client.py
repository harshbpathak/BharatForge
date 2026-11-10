import httpx
import pytest

from bharatforge.github_client import GitHubClient, GitHubError, parse_repository


@pytest.mark.parametrize("value", ["owner/repo", "https://github.com/owner/repo", "https://github.com/owner/repo/", "owner/repo.git"])
def test_valid_repository(value):
    assert parse_repository(value) == "owner/repo"


@pytest.mark.parametrize("value", ["https://evil.com/a/b", "http://github.com/a/b", "https://github.com@evil.com/a/b", "https://github.com/a/b?x=1", "https://github.com/a/b/issues", "a/..", "a/b/c", "", "a/b#frag", "https://github.com:443/a/b", "a/" + "x"*101])
def test_invalid_repository(value):
    with pytest.raises(GitHubError):
        parse_repository(value)


def row(number, pr=False):
    value = {"number":number, "title":"Example", "body":None, "labels":[{"name":"bug"}],
             "created_at":"2026-01-01T00:00:00Z", "updated_at":"2026-01-02T00:00:00Z", "comments":0,
             "html_url":"https://evil.com/untrusted"}
    if pr:
        value["pull_request"] = {}
    return value


def metadata():
    return {"private":False, "description":None, "stargazers_count":10, "open_issues_count":150}


def test_pagination_pr_exclusion_and_parsing():
    paths = []
    def handler(request):
        assert request.url.host == "api.github.com"
        assert request.headers["Authorization"] == "Bearer test-token"
        paths.append(str(request.url))
        if request.url.path.endswith("/issues"):
            page = request.url.params["page"]
            data = [row(i, pr=True) for i in range(1, 101)] if page == "1" else [row(i) for i in range(101, 116)]
            return httpx.Response(200, json=data)
        return httpx.Response(200, json=metadata())
    with GitHubClient("test-token", transport=httpx.MockTransport(handler)) as client:
        repo, issues, warnings = client.fetch("owner/repo", 10)
    assert len(paths) == 3 and len(issues) == 10
    assert issues[0].number == 101 and issues[0].body == ""
    assert issues[0].url == "https://github.com/owner/repo/issues/101"
    assert issues[0].labels == ["bug"] and repo.open_items == 150
    assert not warnings


def test_empty_repository():
    with GitHubClient(transport=httpx.MockTransport(lambda r: httpx.Response(200, json=[] if r.url.path.endswith("/issues") else metadata()))) as client:
        _, issues, warnings = client.fetch("owner/repo")
    assert issues == [] and warnings == []


@pytest.mark.parametrize("status", [401, 403, 404, 429, 500, 301])
def test_api_failures(status):
    calls = []
    def handler(r):
        calls.append(1)
        return httpx.Response(status, text="secret must never appear")
    with GitHubClient(transport=httpx.MockTransport(handler), sleep=lambda _: None) as client:
        with pytest.raises(GitHubError) as error:
            client.fetch("owner/repo")
    assert "secret" not in str(error.value)
    assert len(calls) == (3 if status == 500 else 1)


def test_private_and_invalid_limit():
    with GitHubClient(transport=httpx.MockTransport(lambda _: httpx.Response(200, json={**metadata(), "private":True}))) as client:
        with pytest.raises(GitHubError, match="public"):
            client.fetch("owner/repo")
        with pytest.raises(GitHubError, match="limit"):
            client.fetch("owner/repo", 999)


def test_network_failure_retries():
    calls = []
    def handler(request):
        calls.append(1)
        raise httpx.ConnectError("do not expose", request=request)
    with GitHubClient(transport=httpx.MockTransport(handler), sleep=lambda _:None) as client:
        with pytest.raises(GitHubError, match="could not be reached"):
            client.fetch("owner/repo")
    assert len(calls) == 3
