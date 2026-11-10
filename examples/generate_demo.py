"""Generate the bundled synthetic demo; never presented as live inference."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
now = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)
rows = [
    (101, "Export crashes when CSV contains emoji", "Export crashes when CSV contains emoji. Steps: upload a CSV with emoji, click Export. Expected: download. Actual: TypeError in serializer. Version 1.4, Linux.", "bug", "high", 85.0, 90.0, "A reported export crash affects CSV data containing emoji.", ["Stack trace"], "Reproduce the emoji export path and inspect serializer encoding.", 30),
    (102, "CSV export fails with emoji characters", "CSV export crashes when CSV contains emoji. Upload a CSV with emoji then click Export. TypeError in serializer. Version 1.4, Linux.", "bug", "high", 80.0, 85.0, "A second report describes the same emoji export failure.", ["Minimal CSV attachment"], "Compare with issue #101 before investigating separately.", 25),
    (103, "Add keyboard shortcuts to search", "Feature request: press slash to focus repository search. This would save repeated mouse clicks during triage.", "feature", "low", 45.0, 80.0, "A maintainer requests a keyboard shortcut for search.", ["Accessibility requirements"], "Discuss shortcut conflicts and keyboard accessibility.", 60),
    (104, "Quickstart uses an outdated config name", "The quickstart says API_TOKEN but version 1.4 expects SERVICE_TOKEN. New installations fail until I rename the variable.", "documentation", "medium", 65.0, 85.0, "The quickstart reportedly documents the wrong environment variable.", ["Documentation page URL"], "Verify the variable name and update the quickstart example.", 10),
    (105, "Is self-hosted deployment supported?", "Can I deploy this tool on an internal network? I cannot find a self-hosting guide.", "question", "low", 30.0, 60.0, "A user asks about deployment on an internal network.", ["Deployment constraints"], "Clarify hosting requirements and point to deployment documentation.", 5),
    (106, "Upgrade dependency audit workflow", "Our dependency audit workflow uses an old action version. Please review the current supported version and pin the commit SHA.", "maintenance", "low", 40.0, 65.0, "A workflow maintenance request asks for a dependency audit action update.", ["Current action version"], "Review the action release notes and pin a reviewed commit.", 90),
    (107, "Search times out with 100k records", "Search times out with 100k records after about 30 seconds. Dataset has 100k rows. I have not captured logs. This blocks our weekly triage.", "bug", "high", 75.0, 55.0, "A large dataset reportedly triggers a search timeout.", ["Server logs", "Hardware", "Minimal dataset"], "Request logs and profile search on a comparable large dataset.", 15),
    (108, "Add JSON report export", "We need a JSON report export so our nightly automation can read triage results without parsing Markdown.", "feature", "medium", 60.0, 80.0, "An automation workflow needs a machine-readable export.", ["Required JSON schema"], "Agree a versioned export schema with the requester.", 40),
    (109, "Empty result screen has no guidance", "When search has zero matches, I only see a blank panel. Please show a message and a clear filters action.", "feature", "low", 35.0, 90.0, "An empty search result screen reportedly lacks guidance.", [], "Add an empty-state message with a filter reset action.", 2),
    (110, "Login intermittently returns 500", "Login intermittently returns 500. It happened twice today on version 1.4. I cannot reproduce consistently and have no server logs.", "bug", "high", 80.0, 25.0, "An intermittent login failure is reported with limited diagnostics.", ["Server logs", "Request ID", "Authentication method"], "Request a redacted request ID and server logs before narrowing the cause.", 7),
]
issues = []
severity = {"critical":100, "high":75, "medium":50, "low":25}
for number, title, body, category, level, impact, clarity, summary, missing, action, days in rows:
    age = min(100.0, days / 180 * 100)
    issues.append({"issue": {"number":number, "title":title, "body":body, "labels":[category],
        "created_at":(now-timedelta(days=days)).isoformat(), "updated_at":now.isoformat(), "comments":2,
        "url":f"https://github.com/bharatforge-demo/triage-lab/issues/{number}", "truncated":False},
        "analysis":{"number":number, "category":category, "severity":level, "summary":summary,
        "impact":impact, "reproducibility":clarity, "confidence":.82, "observed_facts":[body.split('. ')[0]],
        "inferred_conclusions":["Maintainer review is needed to confirm scope and impact."],
        "missing_information":missing, "suggested_action":action, "evidence":[body.split('. ')[0]]},
        "priority":{"score":round(.4*severity[level]+.35*impact+.15*clarity+.1*age,2),
                    "severity":float(severity[level]), "impact":impact, "reproducibility":clarity, "age":age}})
report = {"schema_version":"1.0", "mode":"demo", "generated_at":now.isoformat(),
    "repository":{"full_name":"bharatforge-demo/triage-lab", "description":"Synthetic issue backlog for the BharatForge demo. Not a real repository.",
                  "stars":128, "open_items":42, "url":"https://github.com/bharatforge-demo/triage-lab"},
    "issues":issues, "duplicates":[{"first":101,"second":102,"similarity":.83,
        "verdict":{"same_problem":True,"reason":"Both synthetic reports describe emoji CSV export failure with the same serializer error.","confidence":.94}}],
    "overview":{"summary":"This synthetic sample highlights export reliability, search performance, and triage workflow improvements.",
                "observations":["Two export reports may share a root cause; review them together.",
                    "Login and search reports need more diagnostic context before a fix can be scoped.",
                    "Correcting the quickstart variable name could reduce setup friction."]},
    "warnings":["All source data and AI judgments in this demo are synthetic. No API requests were made."],
    "request_count":0,"latency_seconds":0.0,"model":"mock / bundled demo"}
(ROOT / "examples" / "sample_issues.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
