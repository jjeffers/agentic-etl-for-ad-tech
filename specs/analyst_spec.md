# Analyst Agent Specification

## Role Overview
The Analyst resolves generated alerts through Root Cause Triangulation. Its goal is to distinguish between a "Machine" failure (e.g. ETL script error, specification drift) and a "Market" failure (e.g. legitimate supply slowdown) preventing unneeded developer escalation.

## Code & Artifact Generation
- **Cross-Referencing Scripts:** Python logic to scrape or query 3rd-party status pages, API health endpoints, and internal logs (e.g. Elasticsearch/Splunk) simultaneously.
- **Triage Reports:** Markdown/HTML formatted email and Slack summaries detailing the root cause determination.
- **Incident Response Configurations:** Automated API calls to PagerDuty/Jira to update, resolve, or escalate the incident ticket based on findings.

## Guardrails
- **Mandatory Source Citation:** Any conclusion distinguishing "Market" vs "Machine" failure MUST include a direct citation (e.g., a specific log line, a 3rd-party status page URL with timestamp).
- **Anti-Sycophancy Review:** Before routing a conclusion of "Market Downturn" (to avoid debugging), the agent must cross-reference at least two differing data sources (internal logs vs 3rd-party status).
- **Human Sign-off Required:** High cost of error. A human must review and sign off on the Analyst's root cause analysis before any large-scale data backfills or destructive fixes are executed.

## Cost Estimation
- **Model Tier:** High-Capability Model (e.g., GPT-4 / Claude 3 Opus).
- **Token Usage Estimate:** 10k-25k tokens per incident, given the need to digest logs, alerts, and external status pages.
- **Approximate Cost per Run:** ~$0.50 - $1.00 per triage event. Highly cost-effective as it is triggered only upon anomaly detection.

## Verification Subsystem
- **Source Validation Check:** Automated pre-flight check ensuring all URLs and log IDs cited in the Triage Report return a successful 200 response or valid record.
- **Red Team Simulation:** Monthly simulated incidents (where the Analyst is fed a known tricky scenario) to evaluate its capability to perform true root cause analysis and bypass sycophantic confirmation.
- **Triage Feedback Loop:** Human resolution tags on Jira tickets automatically evaluating the Analyst's accuracy over time.
