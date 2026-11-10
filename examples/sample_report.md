# BharatForge — bharatforge\-demo/triage\-lab

Mode: **DEMO** | Model: mock / bundled demo
Generated: 2026-11-01T12:00:00+00:00

> Heuristic prioritization estimate, not a verified prediction of business impact.

Repository-wide open items (issues + pull requests): 42
Open issues analyzed in this sample: 10

## Backlog overview

This synthetic sample highlights export reliability, search performance, and triage workflow improvements\.

**DEMO: synthetic sample, mock analysis; no live AI inference. Links are illustrative.**

- Two export reports may share a root cause; review them together\.
- Login and search reports need more diagnostic context before a fix can be scoped\.
- Correcting the quickstart variable name could reduce setup friction\.

## #101 — Export crashes when CSV contains emoji

https://github.com/bharatforge-demo/triage-lab/issues/101

bug | high | Priority: 74.92/100 | Confidence: 82%

A reported export crash affects CSV data containing emoji\.

Action: Reproduce the emoji export path and inspect serializer encoding\.

Components (0–100): severity 75, impact 85, clarity 90, age 16.67.
Formula: 0.40 × severity + 0.35 × impact + 0.15 × clarity + 0.10 × age (180-day cap).

### Observed facts

- Export crashes when CSV contains emoji

### Inferred conclusions

- Maintainer review is needed to confirm scope and impact\.

### Missing information

- Stack trace

### Source quotations

- Export crashes when CSV contains emoji

## #102 — CSV export fails with emoji characters

https://github.com/bharatforge-demo/triage-lab/issues/102

bug | high | Priority: 72.14/100 | Confidence: 82%

A second report describes the same emoji export failure\.

Action: Compare with issue \#101 before investigating separately\.

Components (0–100): severity 75, impact 80, clarity 85, age 13.89.
Formula: 0.40 × severity + 0.35 × impact + 0.15 × clarity + 0.10 × age (180-day cap).

### Observed facts

- CSV export crashes when CSV contains emoji

### Inferred conclusions

- Maintainer review is needed to confirm scope and impact\.

### Missing information

- Minimal CSV attachment

### Source quotations

- CSV export crashes when CSV contains emoji

## #107 — Search times out with 100k records

https://github.com/bharatforge-demo/triage-lab/issues/107

bug | high | Priority: 65.33/100 | Confidence: 82%

A large dataset reportedly triggers a search timeout\.

Action: Request logs and profile search on a comparable large dataset\.

Components (0–100): severity 75, impact 75, clarity 55, age 8.33.
Formula: 0.40 × severity + 0.35 × impact + 0.15 × clarity + 0.10 × age (180-day cap).

### Observed facts

- Search times out with 100k records after about 30 seconds

### Inferred conclusions

- Maintainer review is needed to confirm scope and impact\.

### Missing information

- Server logs
- Hardware
- Minimal dataset

### Source quotations

- Search times out with 100k records after about 30 seconds

## #110 — Login intermittently returns 500

https://github.com/bharatforge-demo/triage-lab/issues/110

bug | high | Priority: 62.14/100 | Confidence: 82%

An intermittent login failure is reported with limited diagnostics\.

Action: Request a redacted request ID and server logs before narrowing the cause\.

Components (0–100): severity 75, impact 80, clarity 25, age 3.89.
Formula: 0.40 × severity + 0.35 × impact + 0.15 × clarity + 0.10 × age (180-day cap).

### Observed facts

- Login intermittently returns 500

### Inferred conclusions

- Maintainer review is needed to confirm scope and impact\.

### Missing information

- Server logs
- Request ID
- Authentication method

### Source quotations

- Login intermittently returns 500

## #104 — Quickstart uses an outdated config name

https://github.com/bharatforge-demo/triage-lab/issues/104

documentation | medium | Priority: 56.06/100 | Confidence: 82%

The quickstart reportedly documents the wrong environment variable\.

Action: Verify the variable name and update the quickstart example\.

Components (0–100): severity 50, impact 65, clarity 85, age 5.56.
Formula: 0.40 × severity + 0.35 × impact + 0.15 × clarity + 0.10 × age (180-day cap).

### Observed facts

- The quickstart says API\_TOKEN but version 1\.4 expects SERVICE\_TOKEN

### Inferred conclusions

- Maintainer review is needed to confirm scope and impact\.

### Missing information

- Documentation page URL

### Source quotations

- The quickstart says API\_TOKEN but version 1\.4 expects SERVICE\_TOKEN

## #108 — Add JSON report export

https://github.com/bharatforge-demo/triage-lab/issues/108

feature | medium | Priority: 55.22/100 | Confidence: 82%

An automation workflow needs a machine\-readable export\.

Action: Agree a versioned export schema with the requester\.

Components (0–100): severity 50, impact 60, clarity 80, age 22.22.
Formula: 0.40 × severity + 0.35 × impact + 0.15 × clarity + 0.10 × age (180-day cap).

### Observed facts

- We need a JSON report export so our nightly automation can read triage results without parsing Markdown\.

### Inferred conclusions

- Maintainer review is needed to confirm scope and impact\.

### Missing information

- Required JSON schema

### Source quotations

- We need a JSON report export so our nightly automation can read triage results without parsing Markdown\.

## #103 — Add keyboard shortcuts to search

https://github.com/bharatforge-demo/triage-lab/issues/103

feature | low | Priority: 41.08/100 | Confidence: 82%

A maintainer requests a keyboard shortcut for search\.

Action: Discuss shortcut conflicts and keyboard accessibility\.

Components (0–100): severity 25, impact 45, clarity 80, age 33.33.
Formula: 0.40 × severity + 0.35 × impact + 0.15 × clarity + 0.10 × age (180-day cap).

### Observed facts

- Feature request: press slash to focus repository search

### Inferred conclusions

- Maintainer review is needed to confirm scope and impact\.

### Missing information

- Accessibility requirements

### Source quotations

- Feature request: press slash to focus repository search

## #106 — Upgrade dependency audit workflow

https://github.com/bharatforge-demo/triage-lab/issues/106

maintenance | low | Priority: 38.75/100 | Confidence: 82%

A workflow maintenance request asks for a dependency audit action update\.

Action: Review the action release notes and pin a reviewed commit\.

Components (0–100): severity 25, impact 40, clarity 65, age 50.00.
Formula: 0.40 × severity + 0.35 × impact + 0.15 × clarity + 0.10 × age (180-day cap).

### Observed facts

- Our dependency audit workflow uses an old action version

### Inferred conclusions

- Maintainer review is needed to confirm scope and impact\.

### Missing information

- Current action version

### Source quotations

- Our dependency audit workflow uses an old action version

## #109 — Empty result screen has no guidance

https://github.com/bharatforge-demo/triage-lab/issues/109

feature | low | Priority: 35.86/100 | Confidence: 82%

An empty search result screen reportedly lacks guidance\.

Action: Add an empty\-state message with a filter reset action\.

Components (0–100): severity 25, impact 35, clarity 90, age 1.11.
Formula: 0.40 × severity + 0.35 × impact + 0.15 × clarity + 0.10 × age (180-day cap).

### Observed facts

- When search has zero matches, I only see a blank panel

### Inferred conclusions

- Maintainer review is needed to confirm scope and impact\.

### Missing information

None supplied.

### Source quotations

- When search has zero matches, I only see a blank panel

## #105 — Is self\-hosted deployment supported?

https://github.com/bharatforge-demo/triage-lab/issues/105

question | low | Priority: 29.78/100 | Confidence: 82%

A user asks about deployment on an internal network\.

Action: Clarify hosting requirements and point to deployment documentation\.

Components (0–100): severity 25, impact 30, clarity 60, age 2.78.
Formula: 0.40 × severity + 0.35 × impact + 0.15 × clarity + 0.10 × age (180-day cap).

### Observed facts

- Can I deploy this tool on an internal network? I cannot find a self\-hosting guide\.

### Inferred conclusions

- Maintainer review is needed to confirm scope and impact\.

### Missing information

- Deployment constraints

### Source quotations

- Can I deploy this tool on an internal network? I cannot find a self\-hosting guide\.

## Potential duplicate pairs

- [#101](https://github.com/bharatforge-demo/triage-lab/issues/101) / [#102](https://github.com/bharatforge-demo/triage-lab/issues/102): similarity 0.83; Suspected same problem. Confidence 94%. Both synthetic reports describe emoji CSV export failure with the same serializer error\.

## Warnings

- All source data and AI judgments in this demo are synthetic\. No API requests were made\.

AI requests: 0; elapsed request time: 0.00s
