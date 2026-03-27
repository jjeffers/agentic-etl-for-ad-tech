# Architect Agent Specification

## Role Overview
The Integration Architect is responsible for identifying "Publisher Supply Performance" endpoints from 3rd-party Ad-Tech API documentation and mapping them to the internal `reporting_v1` data warehouse schema.

## Code & Artifact Generation
- **Batch Target State Management:** Iteration over a registry (e.g., `targets.json`) of integrations. The agent maintains state memory by checking a local directory (`schemas/`) to determine if an integration has already been analyzed before engaging models.
- **API Extraction Scripts:** Python scripts utilizing `httpx` and `BeautifulSoup` to fetch and parse live documentation from URLs.
- **RAG Prompts:** Generated queries for retrieving reporting endpoint definitions from ingested documentation.
- **JSON Schema Map:** A structured JSON document mapping external API fields to the internal `reporting_v1` columns.
- **Privacy Configuration:** Configuration flags within the JSON schema denoting fields that contain Personally Identifiable Information (PII), specifically household IP addresses.

## Guardrails
- **Privacy Compliance Constraint:** Must explicitly flag any fields containing household IP addresses or other PII for secure hashing/omission. Failure to do so blocks moving to the Engineer deployment phase.
- **Read-Only Discovery:** The agent strictly operates in a read-only discovery mode. It cannot execute code that mutates the target integration or the internal data warehouse.
- **Human In The Loop (HITL) Checkpoint:** All generated target schemas and revenue definitions *must* be approved by Finance/Ops before progressing to the deployment phase. (Reversibility of an error here is Low, cost is Critical).

## Cost Estimation
- **Model Tier:** High-Capability Model (e.g., GPT-4 / Claude 3 Opus).
- **Token Usage Estimate:** Due to retrieving and processing extensive API documentation texts via RAG, expect 30k-60k tokens per new integration schema discovery constraint.
- **Approximate Cost per Run:** ~$0.50 - $1.50 per new source API mapping. This is typically a one-off cost per ad-network or when specification drift occurs.

## Verification Subsystem
- **Syntactic Validation:** The JSON Schema Map must pass 100% data-type validation before human review.
- **Compliance Linter:** An automated static analysis tool that scans the proposed schema mappings for suspected PII fields (regex/keyword matching against `ip`, `address`, `email`, etc.).
- **Drift Simulation Test:** Unit test feeding the Architect an altered fake API document to ensure it flags a schema update requirement appropriately instead of forcefully mapping unmatched fields.
