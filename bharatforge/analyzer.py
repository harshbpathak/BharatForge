"""Orchestrate validated analysis, deterministic scores and duplicate review."""
from datetime import datetime, timezone
import json
from pathlib import Path

from .ai_client import AIError
from .duplicates import confirm_candidate, find_candidates
from .schemas import (AnalysisBatch, AnalysisReport, AnalyzedIssue, BacklogOverview,
                      DuplicatePair)
from .scoring import priority_score


def analyze(repository, issues, ai, warnings=None, threshold=.35, progress=None):
    now = datetime.now(timezone.utc)
    warnings = list(warnings or [])
    analyzed = []
    notify = progress or (lambda fraction, message: None)
    # Three issues per request bounds output consumption and preserves source context.
    for start in range(0, len(issues), 3):
        batch = issues[start:start + 3]
        notify(.1 + .65 * start / max(1, len(issues)), f"Analyzing issues {start + 1}-{start + len(batch)}")
        result = ai.request(
            "Analyze each issue exactly once. Include every input number. Evidence must be "
            "verbatim excerpts. Use empty arrays where the text supplies no facts/evidence. "
            "Assess severity, impact and diagnostic clarity; do not claim verified business impact.",
            [{"number": issue.number, "title": issue.title, "body": issue.body,
              "labels": issue.labels} for issue in batch], AnalysisBatch)
        by_number = {item.number: item for item in result.issues}
        if len(by_number) != len(result.issues) or set(by_number) != {issue.number for issue in batch}:
            raise AIError("BharatCode returned missing, duplicate or unexpected issue numbers.")
        for issue in batch:
            item = by_number[issue.number]
            if any(quote not in issue.title and quote not in issue.body for quote in item.evidence):
                raise AIError("BharatCode returned evidence not present in the issue. Analysis was rejected.")
            analyzed.append(AnalyzedIssue(issue=issue, analysis=item,
                priority=priority_score(item.severity, item.impact, item.reproducibility, issue.created_at, now)))
    duplicates = []
    lookup = {issue.number: issue for issue in issues}
    candidates = find_candidates(issues, threshold)
    for index, candidate in enumerate(candidates):
        notify(.78 + .15 * index / max(1, len(candidates)), "Reviewing potential duplicates")
        try:
            duplicates.append(confirm_candidate(candidate, lookup, ai))
        except AIError:
            duplicates.append(DuplicatePair(first=candidate.first, second=candidate.second,
                                             similarity=candidate.similarity, verdict=None))
            warnings.append("A duplicate candidate could not be reviewed by BharatCode; similarity alone is not confirmation.")
    if analyzed:
        notify(.95, "Writing backlog overview")
        try:
            overview = ai.request("Summarize this analyzed sample, with cautious actionable observations. "
                                  "Do not generalize to the entire repository backlog.",
                [{"number": item.issue.number, "category": item.analysis.category,
                  "severity": item.analysis.severity, "summary": item.analysis.summary,
                  "priority": item.priority.score} for item in analyzed], BacklogOverview, budget=1800)
        except AIError:
            overview = BacklogOverview(summary=f"Analyzed {len(analyzed)} open issues. AI overview unavailable.", observations=[])
            warnings.append("BharatCode overview was unavailable; validated per-issue results are preserved.")
    else:
        overview = BacklogOverview(summary="No open issues found in this repository sample.", observations=[])
    notify(1.0, "Analysis complete")
    return AnalysisReport(mode="live", generated_at=now, repository=repository, issues=analyzed,
                          duplicates=duplicates, overview=overview, warnings=list(dict.fromkeys(warnings)),
                          request_count=ai.request_count, latency_seconds=round(ai.latency_seconds, 2), model=ai.model)


def load_demo():
    path = Path(__file__).resolve().parent.parent / "examples" / "sample_issues.json"
    return AnalysisReport.model_validate_json(path.read_text(encoding="utf-8-sig"))
