# Architect Proof of Concept (PoC) Task List

## 1. Environment & Framework Setup
- [ ] Initialize Python environment.
- [ ] Install required SDKs (`openai` or `anthropic`, `pydantic`, `httpx`, `beautifulsoup4`).
- [ ] Set up API keys in environment variables.

## 2. Ingestion Module (API Extraction)
- [ ] Write a Python script to scrape a sample 3rd-party Ad-Tech API documentation page.
- [ ] (Optional) Set up a local vector store (like ChromaDB) if RAG is necessary for large docs.

## 3. Define the Target Data Contract (Pydantic)
- [ ] Define the `FieldMapping` Pydantic model (`source_api_field`, `target_reporting_v1_column`, `data_type`, `is_pii_or_ip_address`).
- [ ] Define the `APISchemaMap` Pydantic model (`endpoint_url`, `http_method`, `authentication_method`, `mappings`).

## 4. Core Agent Logic & Prompt Engineering
- [ ] Construct the Architect system prompt.
- [ ] Implement the LLM API call using "Structured Outputs" or "Tool Calling" to enforce the Pydantic schema.

## 5. Verification Subsystem (Guardrails)
- [ ] Implement Syntactic Validation (using Pydantic `model_validate_json`).
- [ ] Write Compliance Linter function to assert `is_pii_or_ip_address == True` for fields containing 'ip', 'address', etc.
- [ ] Add automatic retry logic if the linter catches a privacy compliance violation.

## 6. Human-in-the-Loop (HITL) Checkpoint
- [ ] Pretty-print the validated JSON schema map to the console.
- [ ] Add a user input prompt `Finance/Ops: Do you approve this schema mapping? (y/N)`.
- [ ] Handle the approval/rejection branching.

## 7. Drift Simulation Test
- [ ] Run the pipeline end-to-end on a clean sample API document.
- [ ] Run a test case using altered API documentation with a hidden `household_ip` field.
- [ ] Verify the Architect correctly maps and flags the field, or the Compliance Linter catches the hallucination.
