# Observer Agent Specification

## Role Overview
The Observer (The Sentinel) is responsible for real-time telemetry analysis of the incoming ETL data streams to detect "Semantic Drift" and "Silent Failures" (e.g., API returning a 200 OK status but containing empty or malformed data).

## Code & Artifact Generation
- **Telemetry Queries:** SQL query generation for running statistical aggregations over time-series data (e.g., computing a 7-day rolling average of `sum(impressions)`).
- **Alerting Scripts:** Python or native monitoring tool configurations (e.g., Datadog monitors, Airflow SLAs) that execute the telemetry queries and evaluate against defined thresholds.
- **Incident Payload Construction:** Scripts to format alert data into structured JSON payloads for routing to Analysts or PagerDuty/Slack.

## Guardrails
- **Read-Only Database Access:** SQL generated must only contain `SELECT` statements against the production `reporting_v1` schema.
- **Query Timeout Enforcement:** All generated SQL queries must have strict execution timeouts explicitly stated (e.g. `STATEMENT_TIMEOUT = 30000`) to prevent warehouse locking or overload.
- **Strict Threshold Triggers:** The logic must employ rigid threshold-based rules (e.g. trigger an immediate critical alert if `results: []` on a 200 OK). No fuzzy logic is permitted for critical alerts.

## Cost Estimation
- **Model Tier:** Lightweight Model (e.g., Llama 3 8B, Claude 3 Haiku).
- **Token Usage Estimate:** ~1k tokens per hourly check. The queries are mostly templated strings utilizing variables contextually checked against simple assertions.
- **Approximate Cost per Run:** ~$0.001 - $0.005 per run. Very cost-effective for high-frequency (hourly/daily) polling.

## Verification Subsystem
- **Query Explain Validation:** Database `EXPLAIN` plan analysis confirming no full-table scans occur without a date partition filter.
- **Dry-Run Alerting (Synthetic Telemetry):** Injection of synthetic "failing" telemetry data (a mocked drop of >20% revenue) in staging to ensure the alerting logic successfully triggers the incident payload.
- **Alert Payload Validation:** JSON Schema validation ensures the generated alert payload conforms exactly to the downstream Analyst agent's expected input structure.
