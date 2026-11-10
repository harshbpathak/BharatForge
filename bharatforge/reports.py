"""Portable exports; escape issue and model text before embedding in Markdown."""
import html
import re

from .schemas import AnalysisReport


def safe_markdown(text: str) -> str:
    text = html.escape(text, quote=True)
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~\-])", r"\\\1", text)


def issue_url(report, number):
    # Source URLs are derived from a validated repository identifier, never AI text.
    from .github_client import parse_repository
    name = parse_repository(report.repository.full_name)
    return f"https://github.com/{name}/issues/{number}"


def json_report(report: AnalysisReport) -> str:
    return report.model_dump_json(indent=2)


def markdown_report(report: AnalysisReport) -> str:
    esc = safe_markdown
    lines = [f"# BharatForge — {esc(report.repository.full_name)}", "",
             f"Mode: **{report.mode.upper()}** | Model: {esc(report.model)}",
             f"Generated: {report.generated_at.isoformat()}", "",
             "> Heuristic prioritization estimate, not a verified prediction of business impact.", "",
             f"Repository-wide open items (issues + pull requests): {report.repository.open_items}",
             f"Open issues analyzed in this sample: {len(report.issues)}", "",
             "## Backlog overview", "", esc(report.overview.summary), ""]
    if report.mode == "demo":
        lines += ["**DEMO: synthetic sample, mock analysis; no live AI inference. Links are illustrative.**", ""]
    lines += [f"- {esc(item)}" for item in report.overview.observations]
    for item in sorted(report.issues, key=lambda item: -item.priority.score):
        issue, ai, score = item.issue, item.analysis, item.priority
        lines += ["", f"## #{issue.number} — {esc(issue.title)}", "", issue_url(report, issue.number), "",
                  f"{ai.category} | {ai.severity} | Priority: {score.score:.2f}/100 | Confidence: {ai.confidence:.0%}",
                  "", esc(ai.summary), "", f"Action: {esc(ai.suggested_action)}", "",
                  f"Components (0–100): severity {score.severity:g}, impact {score.impact:g}, "
                  f"clarity {score.reproducibility:g}, age {score.age:.2f}.",
                  "Formula: 0.40 × severity + 0.35 × impact + 0.15 × clarity + 0.10 × age (180-day cap)."]
        for label, values in [("Observed facts", ai.observed_facts), ("Inferred conclusions", ai.inferred_conclusions),
                              ("Missing information", ai.missing_information), ("Source quotations", ai.evidence)]:
            lines += ["", f"### {label}", ""] + ([f"- {esc(value)}" for value in values] or ["None supplied."])
    lines += ["", "## Potential duplicate pairs", ""]
    for pair in report.duplicates:
        verdict = pair.verdict
        status = ("Suspected same problem" if verdict.same_problem else "Likely distinct") if verdict else "Unreviewed similarity candidate"
        lines += [f"- [#{pair.first}]({issue_url(report, pair.first)}) / [#{pair.second}]({issue_url(report, pair.second)}): "
                  f"similarity {pair.similarity:.2f}; {status}. " +
                  (f"Confidence {verdict.confidence:.0%}. {esc(verdict.reason)}" if verdict else "AI review unavailable.")]
    if not report.duplicates:
        lines += ["No candidates met the configured threshold."]
    lines += ["", "## Warnings", ""] + ([f"- {esc(warning)}" for warning in report.warnings] or ["None."])
    lines += ["", f"AI requests: {report.request_count}; elapsed request time: {report.latency_seconds:.2f}s", ""]
    return "\n".join(lines)
