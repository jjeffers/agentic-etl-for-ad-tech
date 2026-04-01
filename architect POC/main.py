import os
import json
import httpx
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel, Field

from google import genai
from google.genai import types

class FieldMapping(BaseModel):
    source_api_field: str
    target_reporting_v1_column: str
    data_type: str
    is_pii_or_ip_address: bool = Field(description="MUST be true if the field contains household IPs, addresses, or other personal data.")

class AuthTelemetry(BaseModel):
    auth_endpoints: Optional[List[str]] = Field(description="List of URLs used for token exchange, refresh, or login.")
    placement: str = Field(description="Where the token/key belongs (e.g., 'Header: Authorization', 'Query: api_key').")
    credentials_required: List[str] = Field(description="Specific parameter names required (e.g., ['client_id', 'client_secret']).")
    token_lifecycle: str = Field(description="Description of token expiration periods and refresh rules.")

class APISchemaMap(BaseModel):
    endpoint_url: str
    http_method: str
    authentication_method: str = Field(description="The required authentication mechanism (e.g., OAuth 2.0, API Keys, Bearer Tokens).")
    auth_telemetry: Optional[AuthTelemetry] = Field(description="Detailed telemetry about the authentication, required if authentication is needed.")
    mappings: List[FieldMapping]

class DiscoveryState(BaseModel):
    status: str = Field(description="Must be 'found_endpoint' if the current page contains the schema, 'navigate_to_link' if we need to click a link, or 'failed_missing_docs' if there are no good options.")
    next_url: Optional[str] = Field(description="The exact absolute URL to navigate to next, ONLY if status is 'navigate_to_link'")
    schema_map: Optional[APISchemaMap] = Field(description="The final mapped schema, ONLY if status is 'found_endpoint'")
    confidence_reasoning: str = Field(description="Brief explanation of why you made this routing decision.")


def compliance_linter(schema: APISchemaMap):
    """Guardrail: Ensure IP address/PII fields are strictly flagged."""
    suspicious_terms = ["ip", "address", "user", "device", "email"]
    for mapping in schema.mappings:
        field_lower = mapping.source_api_field.lower()
        if any(term in field_lower for term in suspicious_terms):
            if not mapping.is_pii_or_ip_address:
                raise ValueError(f"Compliance Linter Error: Field '{mapping.source_api_field}' looks like potential PII but is NOT flagged for hashing!")
    
    print("[LINTER PASS] No unflagged PII fields detected.")

def auth_completeness_linter(schema: APISchemaMap):
    """Guardrail: Ensure Auth Telemetry is complete if a complex method is flagged."""
    if schema.authentication_method and schema.authentication_method.lower() not in ["none", "no auth", "unauthenticated", "none required", ""]:
        if not schema.auth_telemetry:
            raise ValueError(f"Auth Completeness Linter Error: Authentication method '{schema.authentication_method}' was identified, but 'auth_telemetry' is missing!")
        
        auth_lower = schema.authentication_method.lower()
        if "oauth" in auth_lower:
            if not schema.auth_telemetry.auth_endpoints:
                raise ValueError("Auth Completeness Linter Error: OAuth detected, but no token exchange 'auth_endpoints' were identified.")
            if not schema.auth_telemetry.credentials_required:
                raise ValueError("Auth Completeness Linter Error: OAuth detected, but no 'credentials_required' (e.g. client_id) were identified.")
    
    print("[LINTER PASS] Auth Telemetry validation passed.")

def fetch_docs_and_links(url_or_path: str) -> dict:
    if url_or_path.startswith("http"):
        # Ad-tech documentation urls change frequently; follow 301/302 redirects
        response = httpx.get(url_or_path, follow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        text_content = soup.get_text(separator="\n", strip=True)[:40000] # Safe token limit 
        
        # Extract links and resolve them to absolute URLs
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            abs_url = urljoin(str(response.url), href)
            # Basic deduplication and keep only standard web links
            if abs_url not in links and abs_url.startswith("http"):
                links.append(abs_url)
                
        return {"text": text_content, "links": links[:100]}
    else:
        if not os.path.exists(url_or_path):
            raise FileNotFoundError(f"Local file {url_or_path} not found.")
        with open(url_or_path, "r") as f:
            return {"text": f.read(), "links": []}

def extract_schema_autonomous(start_url: str, max_depth: int = 10) -> APISchemaMap:
    """Invokes the Gemini Architect as a recursive web crawler agent."""
    client = genai.Client()
    current_url = start_url
    
    prompt = """You are an Autonomous Integration Architect. Your goal is to find and map 'Publisher Supply Performance' or yield reporting API endpoints from data sources.
If the 'Documentation text' contains the actual API schema fields, set status to 'found_endpoint', and populate 'schema_map'. You MUST accurately flag any fields containing IP addresses or similar PII with `is_pii_or_ip_address` = true. You MUST also identify the required authentication mechanism, output it in the `authentication_method` field, and populate the detailed `auth_telemetry` object.
If the text DOES NOT contain the schema fields, review the provided 'Available Links'. Choose the ONE link that is most likely to lead to the publisher reporting/analytics APIs or developer docs, set status to 'navigate_to_link', and populate 'next_url'."""

    for step in range(max_depth):
        print(f"\n[Depth {step+1}/{max_depth}] Crawling: {current_url}")
        page_data = fetch_docs_and_links(current_url)
        
        links_str = "\n".join(page_data["links"])
        contents = f"{prompt}\n\nCurrent URL: {current_url}\nAvailable Links:\n{links_str}\n\nDocumentation text:\n{page_data['text']}"
        
        print("Analyzing with Architect LLM...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DiscoveryState,
                temperature=0.1
            ),
        )
        
        state: DiscoveryState = response.parsed
        if not state:
            raise ValueError("Model failed to return parsed JSON according to DiscoveryState schema.")
            
        print(f"-> Reasoning: {state.confidence_reasoning}")
        print(f"-> Decision: {state.status}")
        
        if state.status == "found_endpoint" and state.schema_map:
            return state.schema_map
        elif state.status == "navigate_to_link" and state.next_url:
            current_url = state.next_url
            continue
        elif state.status == "failed_missing_docs":
            raise ValueError("Agent explicitly failed to find documentation on this path.")
        else:
            raise ValueError(f"Agent returned invalid state configuration: {state.status}")
            
    raise TimeoutError(f"Autonomous extraction exceeded max depth of {max_depth} without finding the schema.")

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
            schema_map = extract_schema_autonomous(url)
            print("\n=== Final Proposed Schema Map ===")
            print(json.dumps(schema_map.model_dump(), indent=2))
            
            print("=== Running Guardrails ===")
            compliance_linter(schema_map)
            auth_completeness_linter(schema_map)
            
            with open(schema_path, "w") as out:
                json.dump(schema_map.model_dump(), out, indent=2)
            print(f"[SUCCESS] Schema mapped and saved to {schema_path}. Pending human approval.")

        except Exception as e:
            print(f"[PIPELINE EXCEPTION] Failed on {name}: {e}")

if __name__ == "__main__":
    main()
