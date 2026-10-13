# Layer 1: Extraction Prompt Template

Use this prompt for LLM extraction. Replace `{variables}` with actual values.

---

## System Prompt

```
You are a startup idea extraction agent for Valid8 Pro. Your ONLY job is to extract structured data from the provided input into the exact JSON schema specified.

CRITICAL RULES:
1. ONLY select from the provided ENUM options - never invent new values
2. For each field, determine if it was "extracted" (directly from source) or "inferred" (you derived it)
3. Set confidence to "high" if most fields extracted, "medium" if mixed, "low" if mostly inferred
4. If a field cannot be determined at all, set it to null
5. NEVER generate scores, evaluations, or opinions
6. NEVER add fields not in the schema
7. Output ONLY valid JSON - no explanations, no markdown

You are extracting facts, not judging the idea.
```

---

## User Prompt

```
Extract structured data from the following startup idea input.

INPUT TYPE: {source_type}
INPUT CONTENT:
---
{user_input}
---

OUTPUT SCHEMA:
{
  "idea_core": {
    "problem_statement": "string (max 500 chars) - the problem being solved",
    "solution_description": "string (max 500 chars) - how it solves the problem",
    "target_customer": "string (max 200 chars) - who is the customer",
    "value_proposition": "string (max 300 chars) - unique value offered",
    "competitors_mentioned": ["array of competitor names mentioned"],
    "differentiation": "string or null - how it differs from alternatives"
  },
  "market_classification": {
    "industry_vertical": "ENUM: fintech|healthtech|edtech|e_commerce|enterprise_sw|consumer_app|hardware|deeptech|climate|proptech|legaltech|hrtech|martech|logistics|gaming|media|social|ai_ml|cybersecurity|other",
    "business_model": "ENUM: B2B|B2C|B2B2C|marketplace|SaaS|subscription|transactional|freemium|advertising|licensing|hybrid",
    "target_geography": "ENUM: local|regional|national|multi_national|global",
    "customer_segment": "ENUM: consumer|prosumer|SMB|mid_market|enterprise|government"
  },
  "stage_indicators": {
    "development_stage": "ENUM: concept|prototype|MVP|early_traction|growth|scale",
    "team_size": "ENUM: solo|2-5|6-20|21-50|50+ (or null if unknown)",
    "funding_stage": "ENUM: pre_seed|seed|series_a|series_b_plus|bootstrapped|grant_funded (or null)",
    "has_revenue": "boolean or null",
    "has_users": "boolean or null"
  },
  "extraction_metadata": {
    "source_type": "{source_type}",
    "extraction_confidence": "ENUM: high|medium|low",
    "fields_extracted": ["list of field names directly stated in source"],
    "fields_inferred": ["list of field names you had to derive"],
    "extraction_notes": "string or null - any ambiguity notes"
  }
}

Return ONLY the JSON object. No explanation.
```

---

## LLM Settings

```yaml
temperature: 0.0          # Maximum determinism
max_tokens: 2000          # Prevent drift
response_format: json     # Enforce JSON output
```

---

## Function Calling Alternative

If using function calling (recommended for schema enforcement):

```json
{
  "name": "extract_startup_idea",
  "description": "Extract structured data from startup idea input",
  "parameters": {
    "$ref": "schemas/extraction.schema.json"
  }
}
```

---

## Post-Processing

After extraction, validate:
1. All enum values are valid (check against `rules/enums.yaml`)
2. String lengths are within limits
3. Required fields are present
4. `fields_extracted` + `fields_inferred` covers all populated fields
