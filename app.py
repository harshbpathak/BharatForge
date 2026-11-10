"""BharatForge's local Streamlit dashboard."""
import pandas as pd
import plotly.express as px
import streamlit as st

from bharatforge.ai_client import AIClient, AIError
from bharatforge.analyzer import analyze, load_demo
from bharatforge.config import ConfigurationError, Settings
from bharatforge.github_client import GitHubClient, GitHubError
from bharatforge.reports import issue_url, json_report, markdown_report

st.set_page_config(page_title="BharatForge · Issue intelligence", page_icon="⚒️", layout="wide")
st.markdown("""<style>
.block-container {max-width:1440px;padding-top:2.4rem;padding-bottom:3rem}
[data-testid="stMetric"] {background:#141c30;border:1px solid #29334b;border-radius:12px;padding:16px}
[data-testid="stMetricLabel"] {color:#aab7d0}
h1 {letter-spacing:-1.8px} h2 {letter-spacing:-.7px}
[data-testid="stForm"] {border-color:#29334b;border-radius:16px}
.stButton>button[kind="primary"] {font-weight:650}
</style>""", unsafe_allow_html=True)  # Static application CSS only.

left, right = st.columns([4, 1])
with left:
    st.caption("OPEN SOURCE  /  MAINTAINER TOOLKIT")
    st.title("⚒ BharatForge")
    st.markdown("Turn a noisy issue backlog into your next clear action.")
with right:
    st.caption("Powered by BharatCode")
    st.link_button("GitHub ↗", "https://github.com/harshbpathak/BharatForge")
st.divider()

with st.form("repository_analysis"):
    st.subheader("Understand your repository")
    repo_col, count_col = st.columns([4, 1])
    repository = repo_col.text_input("Public GitHub repository", placeholder="owner/repo or https://github.com/owner/repo", max_chars=250)
    limit = count_col.selectbox("Latest open issues", [10, 20, 30, 50], index=1)
    with st.expander("Analysis options"):
        threshold = st.slider("Duplicate similarity threshold", .1, .95, .35, .05)
        st.caption("TF-IDF selects up to 8 candidate pairs for AI review. Similarity alone does not establish duplication.")
    submit = st.form_submit_button("Analyze Repository", type="primary")
    st.caption("Read-only · Public repositories · Issue text is sent to BharatCode for analysis")

if st.button("Try Demo", help="Load a bundled synthetic repository with clearly labeled mock analysis. No keys or network required."):
    st.session_state.report = load_demo()

if submit:
    settings = Settings.from_env()
    ai = None
    progress = st.progress(0, text="Validating configuration")
    try:
        settings.validate_live()
        progress.progress(.04, text="Retrieving public GitHub repository")
        with GitHubClient(settings.github_token) as github:
            repo, issues, warnings = github.fetch(repository, limit)
        ai = AIClient(settings)
        result = analyze(repo, issues, ai, warnings, threshold,
                         lambda fraction, message: progress.progress(fraction, text=message))
        st.session_state.report = result
        st.success("Analysis complete. Results refer to the retrieved sample.")
    except (ConfigurationError, GitHubError, AIError) as exc:
        st.error(str(exc))
        if "report" in st.session_state:
            st.info("The previous successful report remains below; it is not a result for this failed request.")
    except Exception:
        st.error("Analysis could not be completed. Check your configuration and retry. No partial analysis was published.")
    finally:
        progress.empty()
        if ai is not None:
            ai.close()

report = st.session_state.get("report")
if report is None:
    st.markdown("### Less triage. More shipping.")
    one, two, three = st.columns(3)
    with one:
        st.subheader("01 / See the signal")
        st.write("Understand categories, severity, and missing context across your issue sample.")
    with two:
        st.subheader("02 / Set priorities")
        st.write("Use a transparent score with visible severity, impact, clarity, and age components.")
    with three:
        st.subheader("03 / Take action")
        st.write("Review duplicate candidates, inspect source evidence, and export your findings.")
    st.info("Start with a public repository, or select Try Demo to explore without API credentials.")
    st.stop()

if report.mode == "demo":
    st.warning("DEMO · Synthetic repository and mock analysis. No live AI inference. Issue links are illustrative.")
else:
    st.caption(f"LIVE · {report.model} · Generated {report.generated_at:%Y-%m-%d %H:%M UTC}")
for warning in report.warnings:
    st.warning(warning)
st.subheader(report.repository.full_name)
st.text(report.repository.description)
confirmed = [pair for pair in report.duplicates if pair.verdict and pair.verdict.same_problem]
unreviewed = [pair for pair in report.duplicates if pair.verdict is None]
metrics = st.columns(5)
metrics[0].metric("Repository stars", f"{report.repository.stars:,}")
metrics[1].metric("Repo open items¹", f"{report.repository.open_items:,}")
metrics[2].metric("Issues analyzed", len(report.issues))
metrics[3].metric("Sample priority ≥70", sum(item.priority.score >= 70 for item in report.issues))
metrics[4].metric("Suspected pairs²", len(confirmed) + len(unreviewed))
st.caption("¹ GitHub repository-wide count includes open pull requests. All other findings apply only to the analyzed sample. "
           "² Includes AI-suspected and unreviewed candidates; no automatic repository changes.")

analytics, explorer, duplicates, exports = st.tabs(["Overview", "Issue explorer", "Duplicate review", "Export report"])
with analytics:
    st.subheader("Backlog briefing")
    st.text(report.overview.summary)
    for observation in report.overview.observations:
        st.text("• " + observation)
    st.caption("Priority is a heuristic prioritization estimate, not a verified prediction of business impact.")
    if report.issues:
        frame = pd.DataFrame([{"Issue": f"#{item.issue.number}", "Title": item.issue.title,
                               "Category": item.analysis.category, "Severity": item.analysis.severity,
                               "Priority": item.priority.score} for item in report.issues])
        a, b = st.columns(2)
        colors = ["#8b9dff", "#63d4c2", "#f6c177", "#c4a7e7", "#eb6f92", "#7793b3"]
        with a:
            st.plotly_chart(px.pie(frame, names="Category", hole=.65, title="Issue categories",
                                   color_discrete_sequence=colors), use_container_width=True)
        with b:
            severity_counts = frame["Severity"].value_counts().reindex(["critical", "high", "medium", "low"], fill_value=0)
            st.plotly_chart(px.bar(x=severity_counts.index, y=severity_counts.values,
                                   title="Severity estimates", labels={"x": "Severity", "y": "Issues"},
                                   color_discrete_sequence=["#8b9dff"]), use_container_width=True)
        st.markdown("#### Priority ranking")
        st.dataframe(frame.sort_values("Priority", ascending=False), hide_index=True, use_container_width=True)
    else:
        st.info("No open issues to analyze. Exports still include repository metadata.")

with explorer:
    search = st.text_input("Search issue titles, bodies, or summaries", max_chars=200)
    a, b = st.columns(2)
    categories = a.multiselect("Categories", ["bug", "feature", "documentation", "question", "maintenance", "other"])
    severities = b.multiselect("Severity", ["critical", "high", "medium", "low"])
    visible = [item for item in report.issues
               if (not categories or item.analysis.category in categories)
               and (not severities or item.analysis.severity in severities)
               and (search.casefold() in (item.issue.title + item.issue.body + item.analysis.summary).casefold())]
    st.caption(f"{len(visible)} issues match")
    for item in sorted(visible, key=lambda item: -item.priority.score):
        issue, ai, score = item.issue, item.analysis, item.priority
        with st.container(border=True):
            st.text(f"#{issue.number} · {issue.title}")
            st.caption(f"{ai.category.upper()} / {ai.severity.upper()} · Priority {score.score:.2f}/100 · Confidence {ai.confidence:.0%}")
            st.text(ai.summary)
            st.text("Suggested action: " + ai.suggested_action)
            if ai.missing_information:
                st.text("Missing information: " + "; ".join(ai.missing_information))
            with st.expander("Evidence & score breakdown"):
                st.text("Observed facts: " + ("; ".join(ai.observed_facts) or "None supplied"))
                st.text("Inferences: " + ("; ".join(ai.inferred_conclusions) or "None supplied"))
                for quote in ai.evidence:
                    st.text('Source quotation: "' + quote + '"')
                st.text(f"Severity {score.severity:g} × 0.40 + impact {score.impact:g} × 0.35 + "
                        f"clarity {score.reproducibility:g} × 0.15 + age {score.age:.2f} × 0.10 = {score.score:.2f}")
                st.caption("Age caps at 180 days. Scores use the report generation timestamp. High priority starts at 70.")
                st.text(f"Comments: {issue.comments} · Labels: {', '.join(issue.labels) or 'none'} · Created: {issue.created_at:%Y-%m-%d}")
                st.text(issue.body or "No issue body supplied.")
            st.link_button("View GitHub issue ↗", issue_url(report, issue.number))

with duplicates:
    st.subheader("Review potential overlaps")
    st.caption("Similarity is a screening signal. BharatCode reviews at most eight pairs; maintainer review is always required.")
    if not report.duplicates:
        st.info("No candidate pairs met the threshold.")
    for pair in report.duplicates:
        with st.container(border=True):
            st.text(f"#{pair.first} ↔ #{pair.second} · TF-IDF similarity {pair.similarity:.0%}")
            if pair.verdict:
                st.text(("Suspected same problem" if pair.verdict.same_problem else "Likely distinct issues")
                        + f" · AI confidence {pair.verdict.confidence:.0%}")
                st.text(pair.verdict.reason)
            else:
                st.warning("AI review unavailable. This is an unconfirmed similarity candidate.")
            a, b = st.columns(2)
            a.link_button(f"Open #{pair.first} ↗", issue_url(report, pair.first))
            b.link_button(f"Open #{pair.second} ↗", issue_url(report, pair.second))

with exports:
    st.subheader("Bring the findings to your workflow")
    st.write("Export a snapshot with source links, score components, evidence, and analysis provenance.")
    a, b = st.columns(2)
    a.download_button("Download JSON", json_report(report), "bharatforge-analysis.json", "application/json")
    b.download_button("Download Markdown", markdown_report(report), "bharatforge-report.md", "text/markdown")
    st.caption(f"{report.request_count} AI request attempts · {report.latency_seconds:.2f}s approximate request latency · Mode: {report.mode}")
st.divider()
st.caption("BharatForge · Built for BharatCode Build League 2026 · MIT licensed · Human judgment stays in the loop")
