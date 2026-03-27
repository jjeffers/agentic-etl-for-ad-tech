import os
import json
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel, Field

# Using the official gemini sdk
from google import genai
from google.genai import types

class FieldMapping(BaseModel):
    source_api_field: str
    target_reporting_v1_column: str
    data_type: str
    is_pii_or_ip_address: bool = Field(description="MUST be true if the field contains household IPs, addresses, or other personal data.")

class APISchemaMap(BaseModel):
    endpoint_url: str
    http_method: str
    mappings: List[FieldMapping]

def extract_schema(docs: str) -> APISchemaMap:
    """Invokes the Gemini Architect to build a JSON Schema Map from docs."""
    print("Connecting to Gemini...")
    client = genai.Client() # Loads GEMINI_API_KEY from environment
    
    prompt = """You are the Integration Architect. Your job is to extract 'Publisher Supply Performance' reporting endpoints 
from the provided documentation and map their fields to our internal data warehouse schema (reporting_v1).
You MUST accurately flag any fields containing IP addresses or similar PII with `is_pii_or_ip_address` = true."""
    
    # We use gemini-2.5-flash for accurate JSON structured outputs
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"{prompt}\n\nDocumentation text:\n{docs}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=APISchemaMap,
            temperature=0.1
        ),
    )
    
    if not response.parsed:
        raise ValueError("Model failed to return parsed JSON according to schema.")
        
    return response.parsed

def compliance_linter(schema: APISchemaMap):
    """Guardrail: Ensure IP address/PII fields are strictly flagged."""
    suspicious_terms = ["ip", "address", "user", "device", "email"]
    for mapping in schema.mappings:
        field_lower = mapping.source_api_field.lower()
        if any(term in field_lower for term in suspicious_terms):
            if not mapping.is_pii_or_ip_address:
                raise ValueError(f"Compliance Linter Error: Field '{mapping.source_api_field}' looks like potential PII but is NOT flagged for hashing!")
    
    print("[LINTER PASS] No unflagged PII fields detected.")

def fetch_docs(url_or_path: str) -> str:
    if url_or_path.startswith("http"):
        print(f"Fetching from {url_or_path}...")
        # Ad-tech documentation urls change frequently; follow 301/302 redirects
        response = httpx.get(url_or_path, follow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(separator="\n", strip=True)[:50000] # Safe token limit
    else:
        if not os.path.exists(url_or_path):
            raise FileNotFoundError(f"Local file {url_or_path} not found.")
        with open(url_or_path, "r") as f:
            return f.read()

def main():
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: Please put your valid GEMINI_API_KEY inside the .env file and run again.")
        return
        
    targets_file = "targets.json"
    if not os.path.exists(targets_file):
        print(f"Error: {targets_file} not found. Please provide a list of target APIs.")
        return

    with open(targets_file, "r") as f:
        targets = json.load(f)

    os.makedirs("schemas", exist_ok=True)

    for target in targets:
        name = target.get("name")
        url = target.get("url")
        schema_path = f"schemas/{name.lower()}_schema.json"

        print(f"\n--- Processing Integration: {name} ---")

        if os.path.exists(schema_path):
            print(f"Output already exists for '{name}' at {schema_path}. Skipping analysis to preserve memory state.")
            continue

        try:
            print(f"Fetching documentation from {url}...")
            docs = fetch_docs(url)
            print("Analyzing API Documentation with Architect LLM...")
            
            schema_map = extract_schema(docs)
            print("=== Proposed Schema Map ===")
            print(json.dumps(schema_map.model_dump(), indent=2))
            
            print("=== Running Guardrails ===")
            compliance_linter(schema_map)
            
            with open(schema_path, "w") as out:
                json.dump(schema_map.model_dump(), out, indent=2)
            print(f"[SUCCESS] Schema mapped and saved to {schema_path}. Pending human approval.")

        except Exception as e:
            print(f"[PIPELINE EXCEPTION] Failed on {name}: {e}")

if __name__ == "__main__":
    main()
