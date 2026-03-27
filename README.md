# agentic-etl-for-ad-tech
Example specification of an ETL process creation, deployment, and montitoring for ingestion of 3rd party platforms.

# SentinelData: Agentic ETL & Observability for Ad-Tech

## Project Overview
**SentinelData** is a multi-agent system designed to automate the lifecycle of 3rd-party advertising technology (Ad-Server) data integration. It manages the discovery, deployment, and semantic monitoring of publisher supply performance data into an in-house data warehouse.

### The Problem
Traditional ETL maintenance in Ad-Ops is plagued by "Silent Failures" (e.g., API permission changes resulting in 200 OK status but empty data) and "Attribution Drift." Manual triage of these issues is slow, leading to delayed business decisions and financial reporting errors.

---

## 1. System Architecture
SentinelData decomposes the workflow into specialized agents to balance cost, speed, and reasoning depth.

| Agent | Role | Model Tier | Tools |
| :--- | :--- | :--- | :--- |
| **Architect** | API Research & Schema Mapping | **High-Capability** | Search, RAG (API Docs) |
| **Engineer** | Code Generation & Deployment | **Balanced** | Python, SQL, Git |
| **Observer** | Real-time Telemetry Analysis | **Lightweight** | SQL, Statistics Tooling |
| **Analyst** | Root Cause Triangulation | **High-Capability** | Search, Slack/Email API |

### Workflow Decomposition
1. **Discovery:** Architect researches 3rd-party docs to map supply performance endpoints.
2. **Review:** **[Human Checkpoint]** Finance/Ops approves the target schema and revenue definitions.
3. **Deployment:** Engineer generates and deploys the ETL process to the orchestration framework.
4. **Monitoring:** Observer monitors hourly ingestion for anomalies (e.g., >20% revenue drop).
5. **Triage:** Analyst determines if failures are "Machine" (ETL error) or "Market" (supply slowdown).

---

## 2. Agent Specifications (Deep Dive)

Detailed standalone specifications for each agent have been generated. They include breakdowns of code to generate, guardrails, costs, and robust verification subsystems for each role:

* [**The Integration Architect**](./specs/architect_spec.md): Identify "Publisher Supply Performance" endpoints and map to `reporting_v1` warehouse schema.
* [**The Engineer**](./specs/engineer_spec.md): Translate schema maps into executable ETL code and deployment configs.
* [**The Observer (The Sentinel)**](./specs/observer_spec.md): Perform real-time telemetry analysis to detect "Semantic Drift" and "Silent Failures."
* [**The Analyst**](./specs/analyst_spec.md): Resolve alerts through Root Cause Triangulation to differentiate between "Machine" and "Market" failures.

---

## 3. Trust Boundary & Risk Map
We utilize a "Human-in-the-Loop" (HITL) strategy for non-reversible or high-financial-impact tasks.

| Sub-task | Cost of Error | Reversibility | Oversight Level |
| :--- | :--- | :--- | :--- |
| **Schema Mapping** | **CRITICAL** | Low (Corrupts Hist. Data) | **Human Review Required** |
| **API Research** | Low | High | Automated w/ Sampling |
| **Root Cause Analysis** | High | High (Reporting Error) | **Human Sign-off Required** |
| **Code Generation** | Medium | High (Git Revert) | Automated (Unit Tested) |

---

## 4. Failure Mode Analysis (FMA)
* **Specification Drift:** 3rd party changes field names (e.g., `pub_id` → `publisher_uid`).
    * *Detection:* Observer detects 100% null-rate in target column.
    * *Mitigation:* Architect re-reads docs and submits a "Patch Pull Request."
* **Sycophantic Confirmation:** Agent incorrectly blames a "Market Downturn" to avoid debugging.
    * *Mitigation:* Analyst is forced to cross-reference internal logs against external 3rd-party status pages.

---

## 5. Cost & Economic Model
By utilizing **Lightweight models** for high-frequency monitoring and **High-Capability models** for intermittent reasoning, SentinelData achieves a massive ROI over human-only operations.

* **Cost per Daily Cycle:** ~$0.15 (at current API pricing).
* **Scaling:** 10,000 active integrations cost ~$1,500/day.
* **Break-even:** The cost of one Ad-Ops Lead ($150k/year) sustains ~1,000 active, self-healing integrations.

---

## 6. Skills Demonstrated
This specification evidences five market-premium AI skills:
* **Specification Precision:** Converting vague Ad-Tech requirements into rigid data contracts.
* **Evaluation Design:** Defining statistical thresholds for "Silent Failure" detection.
* **Decomposition for Delegation:** Modularizing the system to prevent hallucination propagation.
* **Trust Boundary Design:** Identifying the "One-Way Doors" where human oversight is mandatory.
* **Cost Economics:** Strategic model-tier assignment based on task complexity.
