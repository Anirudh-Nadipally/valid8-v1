"""
Layer 1: LLM Extraction Service
Extracts structured data from user input using Gemini with temperature=0
"""

import json
import os
import re
from typing import Dict, Any, Optional
from pathlib import Path

# Get the directory where this module is located
MODULE_DIR = Path(__file__).parent


def load_extraction_schema() -> Dict[str, Any]:
    """Load the extraction schema from JSON file"""
    schema_path = MODULE_DIR / 'schemas' / 'extraction.schema.json'
    with open(schema_path, 'r') as f:
        return json.load(f)


def get_extraction_prompt(source_type: str, user_input: str) -> str:
    """Generate the extraction prompt for the LLM"""
    return f"""Extract structured data from the following startup idea input.

INPUT TYPE: {source_type}
INPUT CONTENT:
---
{user_input}
---

OUTPUT SCHEMA:
{{
  "idea_core": {{
    "problem_statement": "string (max 500 chars) - the problem being solved",
    "solution_description": "string (max 500 chars) - how it solves the problem",
    "target_customer": "string (max 200 chars) - who is the customer",
    "value_proposition": "string (max 300 chars) - unique value offered",
    "competitors_mentioned": ["array of competitor names mentioned"],
    "differentiation": "string or null - how it differs from alternatives"
  }},
  "market_classification": {{
    "industry_vertical": "ENUM: fintech|healthtech|edtech|e_commerce|enterprise_sw|consumer_app|hardware|deeptech|climate|proptech|legaltech|hrtech|martech|logistics|gaming|media|social|ai_ml|cybersecurity|other",
    "business_model": "ENUM: B2B|B2C|B2B2C|marketplace|SaaS|subscription|transactional|freemium|advertising|licensing|hybrid",
    "target_geography": "ENUM: local|regional|national|multi_national|global",
    "customer_segment": "ENUM: consumer|prosumer|SMB|mid_market|enterprise|government"
  }},
  "stage_indicators": {{
    "development_stage": "ENUM: concept|prototype|MVP|early_traction|growth|scale",
    "team_size": "ENUM: solo|2-5|6-20|21-50|50+ (or null if unknown)",
    "funding_stage": "ENUM: pre_seed|seed|series_a|series_b_plus|bootstrapped|grant_funded (or null)",
    "has_revenue": "boolean or null",
    "has_users": "boolean or null"
  }},
  "extraction_metadata": {{
    "source_type": "{source_type}",
    "extraction_confidence": "ENUM: high|medium|low",
    "fields_extracted": ["list of field names directly stated in source"],
    "fields_inferred": ["list of field names you had to derive"],
    "extraction_notes": "string or null - any ambiguity notes"
  }}
}}

Return ONLY the JSON object. No explanation."""


EXTRACTION_SYSTEM_PROMPT = """You are a startup idea extraction agent for Valid8 Pro. Your ONLY job is to extract structured data from the provided input into the exact JSON schema specified.

CRITICAL RULES:
1. ONLY select from the provided ENUM options - never invent new values
2. For each field, determine if it was "extracted" (directly from source) or "inferred" (you derived it)
3. Set confidence to "high" if most fields extracted, "medium" if mixed, "low" if mostly inferred
4. If a field cannot be determined at all, set it to null
5. NEVER generate scores, evaluations, or opinions
6. NEVER add fields not in the schema
7. Output ONLY valid JSON - no explanations, no markdown

You are extracting facts, not judging the idea."""


class Extractor:
    """Layer 1: LLM-based extraction service"""
    
    def __init__(self, gemini_client):
        """
        Initialize the extractor with a Gemini client
        
        Args:
            gemini_client: Instance of GeminiClient from services.py
        """
        self.client = gemini_client
        self.schema = load_extraction_schema()
    
    def extract(
        self, 
        title: str,
        problem: str,
        solution: str,
        target_audience: str = "",
        unique_value: str = "",
        additional_context: str = "",
        source_type: str = "form_input"
    ) -> Dict[str, Any]:
        """
        Extract structured data from user input
        
        Args:
            title: Idea title
            problem: Problem description
            solution: Solution description
            target_audience: Target audience
            unique_value: Unique value proposition / moat
            additional_context: Any additional context (e.g., from PDF)
            source_type: Type of source (form_input, pitch_deck, etc.)
            
        Returns:
            Extracted data matching extraction.schema.json
        """
        # Construct the user input text
        user_input = f"""
Title: {title}
Problem: {problem}
Solution: {solution}
Target Audience: {target_audience}
Unique Value: {unique_value}
"""
        if additional_context:
            user_input += f"\nAdditional Context:\n{additional_context}"
        
        # Generate the extraction prompt
        prompt = get_extraction_prompt(source_type, user_input)
        
        # Call LLM with temperature=0 for determinism
        response = self.client.generate_completion(
            EXTRACTION_SYSTEM_PROMPT,
            prompt,
            temperature=0.0
        )
        
        # Parse the response
        extracted = self._parse_response(response)
        
        # Ensure all required fields are present
        extracted = self._fill_defaults(extracted, source_type)
        
        return extracted
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response, handling markdown code blocks"""
        # Strip markdown code blocks if present
        match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
        if match:
            response = match.group(1)
        else:
            match = re.search(r"```\s*(.*?)\s*```", response, re.DOTALL)
            if match:
                response = match.group(1)
        
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            print(f"Failed to parse extraction response: {e}")
            print(f"Response was: {response[:500]}")
            # Return a minimal valid structure
            return self._get_default_extraction()
    
    def _get_default_extraction(self) -> Dict[str, Any]:
        """Return a default extraction structure"""
        return {
            "idea_core": {
                "problem_statement": "",
                "solution_description": "",
                "target_customer": "",
                "value_proposition": "",
                "competitors_mentioned": [],
                "differentiation": None
            },
            "market_classification": {
                "industry_vertical": "other",
                "business_model": "B2B",
                "target_geography": "national",
                "customer_segment": "SMB"
            },
            "stage_indicators": {
                "development_stage": "concept",
                "team_size": None,
                "funding_stage": None,
                "has_revenue": None,
                "has_users": None
            },
            "extraction_metadata": {
                "source_type": "form_input",
                "extraction_confidence": "low",
                "fields_extracted": [],
                "fields_inferred": [],
                "extraction_notes": "Extraction failed, using defaults"
            }
        }
    
    def _fill_defaults(self, extracted: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """Fill in any missing required fields with defaults"""
        defaults = self._get_default_extraction()
        defaults["extraction_metadata"]["source_type"] = source_type
        
        # Deep merge with defaults
        result = self._deep_merge(defaults, extracted)
        
        return result
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries, with override taking precedence"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            elif value is not None:
                result[key] = value
        return result
