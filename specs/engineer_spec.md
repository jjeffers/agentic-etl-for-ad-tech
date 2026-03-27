# Engineer Agent Specification

## Role Overview
The Engineer agent handles the mechanical translation of the Architect's approved JSON Schema Map into executable code, and deploys the ETL processes into the orchestration framework.

## Code & Artifact Generation
- **ETL Extraction Scripts:** Python modules to pull data from the 3rd-party Ad-Server APIs factoring in pagination, rate-limiting, and authentication.
- **Data Transformation Scripts:** Python (Pandas/Polars) or SQL pipelines to parse the extracted API payload, apply privacy hashing to flagged PII (IP addresses), and cast to internal `reporting_v1` types.
- **Data Loading Scripts:** SQL DML statements (e.g. `COPY` or `MERGE`) to safely upsert the processed data into the warehouse.
- **Orchestration Configs:** Airflow DAGs, Prefect Flows, or dbt model configurations governing scheduling (e.g., hourly runs).

## Guardrails
- **Sandboxed Execution:** Code must be deployed and executed in a sandboxed staging environment first.
- **Secret Management Enforcement:** The generated code must utilize the platform's secret manager (e.g. AWS Secrets Manager, HashiCorp Vault). Direct hardcoding of API keys fails CI immediately.
- **Data Mutation Restrictions:** DML generated is strictly limited to inserting/upserting to predefined partitions in the `reporting_v1` schema. `DROP` or broadly scoped `DELETE` statements are explicitly prohibited.

## Cost Estimation
- **Model Tier:** Balanced Model (e.g., GPT-4o-mini / Claude 3.5 Sonnet / Llama 3).
- **Token Usage Estimate:** 5k-15k tokens to generate extraction and loading boilerplate based on the mapping schema.
- **Approximate Cost per Run:** ~$0.05 - $0.20 per deployment cycle.

## Verification Subsystem
- **Unit Testing Framework:** Generation of `pytest` scripts mocking API responses (including empty inputs and 500 errors) to ensure extraction scripts fail gracefully.
- **Dry-Run Target Validation:** The staging deployment must complete a dry-run sync over a 1-hour window, verifying that the output row count and column structure exactly match the Architect's schema.
- **PII Hashing Audit:** An automated check in staging to ensure fields flagged by the Architect (like IP address) are hashed (e.g. SHA-256) and not present as plaintext in the sample load.
