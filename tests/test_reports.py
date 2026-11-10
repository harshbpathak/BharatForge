import json
from bharatforge.analyzer import load_demo
from bharatforge.reports import json_report, markdown_report, safe_markdown
from bharatforge.schemas import AnalysisReport


def test_json_roundtrip_and_provenance():
    report = load_demo()
    raw = json_report(report)
    assert AnalysisReport.model_validate_json(raw) == report
    assert json.loads(raw)["mode"] == "demo"
    assert "api_key" not in raw


def test_markdown_contains_source_and_breakdown():
    text = markdown_report(load_demo())
    for value in ["DEMO", "synthetic", "180-day", "Source quotations", "https://github.com/bharatforge-demo/triage-lab/issues/101", "AI requests: 0"]:
        assert value in text


def test_unsafe_content_is_escaped():
    value = safe_markdown('<script>alert(1)</script> [click](https://evil.com) ![img](x)')
    assert "<script>" not in value
    assert "\\[click\\]\\(" in value
    report = load_demo()
    report.issues[0].analysis.summary = '<img src=x onerror=alert(1)>'
    assert "<img" not in markdown_report(report)
