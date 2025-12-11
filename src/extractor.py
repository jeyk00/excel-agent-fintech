import os
import json
from typing import Optional
from openai import OpenAI
from pydantic import ValidationError
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.models import CompanyReport

load_dotenv()


@retry(
    retry=retry_if_exception_type(Exception), # Retry on any exception for now
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=15, max=120), # Gentler backoff: starts at 15s, then 30s, 60s...
    reraise=True
)
def extract_data(markdown_text: str, model_name: str = "gpt-4o") -> CompanyReport:
    """
    Extracts structured financial data from markdown text using an LLM.
    
    Args:
        markdown_text (str): The financial report in markdown format.
        model_name (str): The LLM model to use (default: gpt-4o).
        
    Returns:
        CompanyReport: The extracted structured data.
    """
    # Auto-configure base_url for DeepSeek or Gemini
    base_url = os.getenv("OPENAI_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY") # Default to OpenAI Key
    
    if "deepseek" in model_name.lower():
        if not base_url:
            base_url = "https://api.deepseek.com"
            print(f"Using DeepSeek Base URL: {base_url}")
        # DeepSeek uses OpenAI-compatible API key, usually same env var or DEEPSEEK_API_KEY
        if not api_key:
             api_key = os.getenv("DEEPSEEK_API_KEY")
            
    elif "gemini" in model_name.lower():
        # Gemini OpenAI compatibility
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or OPENAI_API_KEY not found.")
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        print(f"Using Gemini Base URL: {base_url}")

    if not api_key:
        raise ValueError("API Key not found. Set OPENAI_API_KEY or GEMINI_API_KEY.")

    client = OpenAI(api_key=api_key, base_url=base_url)

    # System prompt to guide the LLM
    system_prompt = """
    You are an expert financial analyst. Your task is to extract structured financial data from the provided financial report (Markdown).
    
    Target Structure:
    You MUST return a SINGLE JSON object that matches the following structure exactly:
    
    {
        "company_name": "string",
        "reporting_currency": "string (e.g., PLN, USD)",
        "reporting_unit": "string (e.g., thousands, millions, units)",
        "periods": [
            {
                "period_end_date": "YYYY-MM-DD",
                "revenue": float (Przychody),
                "cogs": float (Koszt własny sprzedaży),
                "ebit": float (Zysk operacyjny),
                "depreciation_amortization": float (Amortyzacja),
                "net_income": float (Zysk netto),
                "assets": float (Aktywa razem - Total Assets),
                "liabilities": float (Zobowiązania razem - Total Liabilities only, DO NOT INCLUDE EQUITY),
                "equity": float (Kapitał własny - Total Equity),
                "ocf": float (Przepływy pieniężne z działalności operacyjnej),
                "shares_outstanding": float (Liczba akcji - UNITS),
                "total_debt": float (Zadłużenie odsetkowe: Kredyty + Obligacje + Leasing),
                "cash_and_equivalents": float (Środki pieniężne)
            }
        ]
    }
    
    Rules:
    1. The output MUST be a single JSON object with a "periods" list.
    2. Use EXACT keys provided above.
    3. Extract data for ALL available reporting periods found in the text.
    4. If a value is negative in the report (e.g., loss), ensure it is negative in the JSON.
    5. **CRITICAL ACCOUNTING CHECK**:
       - `Assets` MUST EQUAL `Liabilities` + `Equity` (approximate tolerance ok).
       - In Polish reports, "Pasywa" = Total Liabilities & Equity. Do NOT put "Pasywa" into the "liabilities" field.
       - "Zobowiązania" = Liabilities. "Kapitał własny" = Equity.
       - Verify that `assets` ≈ `liabilities` + `equity` before responding. if they don't match, you extracted the wrong lines.
    6. SHARES OUTSTANDING: Extract the Weighted Average Number of Shares. If "in thousands", multiply by 1,000.
    7. TOTAL DEBT: Sum of Interest-Bearing Debt (Loans, Bonds, Leases). Do not include trade payables.
    8. Return ONLY valid JSON.
    """

    print(f"Sending request to {model_name}...")
    
    # We might need to truncate the text if it's too long, but GPT-4o has a large context window (128k).
    # LlamaParse output can be large, so let's be mindful. 
    # For now, we send the whole thing.
    
    # DeepSeek Reasoner (R1) and other reasoning models might output <think> blocks
    # or might not support response_format={"type": "json_object"} strictly with reasoning.
    # We'll try to use it, but also clean the output.
    
    try:
        # Check if we are using a DeepSeek model (heuristic)
        is_deepseek = "deepseek" in model_name.lower()
        
        # For DeepSeek Reasoner, we might want to avoid enforcing json_object if it interferes with reasoning,
        # but usually it's fine if we parse robustly.
        # However, let's keep it simple: try standard, if fails or has extra text, clean it.
        
        params = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract data from this report:\n\n{markdown_text}"}
            ],
            "temperature": 0
        }
        
        # Only add response_format if not explicitly a reasoner that might break, 
        # or if we trust the provider. GPT-4o supports it well. 
        # DeepSeek V3 supports it. R1 might be chatty.
        if "reasoner" not in model_name.lower():
             params["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**params)
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Received empty response from LLM.")
            
        print("Received response from LLM. Parsing JSON...")
        
        # Clean potential <think> blocks or markdown formatting
        cleaned_content = _clean_json_text(content)
        
        print(f"DEBUG RAW JSON:\n{cleaned_content[:500]}... (truncated)\n") # Log start of JSON for debugging
        
        data = json.loads(cleaned_content)
        
        # Filter out invalid periods (where critical fields are None)
        if "periods" in data and isinstance(data["periods"], list):
            valid_periods = []
            required_fields = ["revenue", "cogs", "ebit", "net_income", "assets", "liabilities", "equity", "ocf", "shares_outstanding", "total_debt", "cash_and_equivalents"]
            
            for p in data["periods"]:
                # Check if all required fields are present and not None
                if all(p.get(field) is not None for field in required_fields):
                     valid_periods.append(p)
                else:
                    missing = [field for field in required_fields if p.get(field) is None]
                    print(f"Warning: Dropping incomplete period: {p.get('period_end_date', 'Unknown Date')}. Missing: {missing}")
            
            data["periods"] = valid_periods
        
        # Validate with Pydantic
        report = CompanyReport(**data)
        return report

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Cleaned Content: {cleaned_content}")
        raise

    except ValidationError as e:
        print(f"Validation Error: {e}")
        raise
    except Exception as e:
        print(f"Extraction Error: {e}")
        raise

def _clean_json_text(text: str) -> str:
    """
    Cleans the LLM response to extract just the JSON part.
    Removes <think>...</think> blocks and ```json ... ``` markers.
    """
    import re
    
    # Remove <think> blocks (DeepSeek R1)
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Find the first '{' and last '}'
    start = text.find('{')
    end = text.rfind('}')
    
    if start != -1 and end != -1:
        return text[start:end+1]
    
    return text.strip()

if __name__ == "__main__":
    # Test block
    import sys
    
    if len(sys.argv) > 1:
        md_path = sys.argv[1]
        model_name = sys.argv[2] if len(sys.argv) > 2 else "deepseek-reasoner" # Default to deepseek-reasoner for testing if not provided, or gpt-4o if we prefer. Let's default to deepseek-reasoner since user asked.
        
        if os.path.exists(md_path):
            with open(md_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            try:
                report = extract_data(text, model_name=model_name)
                print("\n--- Extracted Data ---")
                print(report.model_dump_json(indent=2))
            except Exception as e:
                print(f"Failed: {e}")
        else:
            print(f"File not found: {md_path}")
    else:
        print("Usage: python -m src.extractor <path_to_markdown> [model_name]")
