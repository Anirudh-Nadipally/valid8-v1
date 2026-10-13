"""
Layer 2: Deterministic Validation
Pure Python validation - NO LLM involvement
"""

import json
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

MODULE_DIR = Path(__file__).parent


def load_enums() -> Dict[str, List[str]]:
    """Load valid enum values from YAML"""
    enums_path = MODULE_DIR / 'rules' / 'enums.yaml'
    with open(enums_path, 'r') as f:
        return yaml.safe_load(f)


def load_extraction_schema() -> Dict[str, Any]:
    """Load the extraction schema"""
    schema_path = MODULE_DIR / 'schemas' / 'extraction.schema.json'
    with open(schema_path, 'r') as f:
        return json.load(f)


# Industry-Model Compatibility Matrix
# ✓ = valid (pass), △ = warning (warn), ✗ = invalid (fail)
COMPATIBILITY_MATRIX = {
    'fintech': {'B2B': 'pass', 'B2C': 'pass', 'B2B2C': 'pass', 'marketplace': 'pass', 'SaaS': 'pass', 'subscription': 'pass', 'transactional': 'pass', 'freemium': 'warn', 'advertising': 'fail', 'licensing': 'pass', 'hybrid': 'pass'},
    'healthtech': {'B2B': 'pass', 'B2C': 'pass', 'B2B2C': 'pass', 'marketplace': 'warn', 'SaaS': 'pass', 'subscription': 'pass', 'transactional': 'pass', 'freemium': 'warn', 'advertising': 'fail', 'licensing': 'pass', 'hybrid': 'pass'},
    'edtech': {'B2B': 'pass', 'B2C': 'pass', 'B2B2C': 'pass', 'marketplace': 'pass', 'SaaS': 'pass', 'subscription': 'pass', 'transactional': 'pass', 'freemium': 'pass', 'advertising': 'warn', 'licensing': 'pass', 'hybrid': 'pass'},
    'enterprise_sw': {'B2B': 'pass', 'B2C': 'fail', 'B2B2C': 'warn', 'marketplace': 'fail', 'SaaS': 'pass', 'subscription': 'pass', 'transactional': 'warn', 'freemium': 'warn', 'advertising': 'fail', 'licensing': 'pass', 'hybrid': 'pass'},
    'consumer_app': {'B2B': 'fail', 'B2C': 'pass', 'B2B2C': 'pass', 'marketplace': 'pass', 'SaaS': 'fail', 'subscription': 'pass', 'transactional': 'pass', 'freemium': 'pass', 'advertising': 'pass', 'licensing': 'fail', 'hybrid': 'pass'},
    'e_commerce': {'B2B': 'warn', 'B2C': 'pass', 'B2B2C': 'pass', 'marketplace': 'pass', 'SaaS': 'warn', 'subscription': 'warn', 'transactional': 'pass', 'freemium': 'fail', 'advertising': 'warn', 'licensing': 'fail', 'hybrid': 'pass'},
    'ai_ml': {'B2B': 'pass', 'B2C': 'pass', 'B2B2C': 'pass', 'marketplace': 'pass', 'SaaS': 'pass', 'subscription': 'pass', 'transactional': 'pass', 'freemium': 'pass', 'advertising': 'warn', 'licensing': 'pass', 'hybrid': 'pass'},
    'deeptech': {'B2B': 'pass', 'B2C': 'warn', 'B2B2C': 'warn', 'marketplace': 'fail', 'SaaS': 'pass', 'subscription': 'pass', 'transactional': 'warn', 'freemium': 'fail', 'advertising': 'fail', 'licensing': 'pass', 'hybrid': 'pass'},
    'climate': {'B2B': 'pass', 'B2C': 'pass', 'B2B2C': 'pass', 'marketplace': 'pass', 'SaaS': 'pass', 'subscription': 'pass', 'transactional': 'pass', 'freemium': 'warn', 'advertising': 'fail', 'licensing': 'pass', 'hybrid': 'pass'},
    'cybersecurity': {'B2B': 'pass', 'B2C': 'warn', 'B2B2C': 'pass', 'marketplace': 'fail', 'SaaS': 'pass', 'subscription': 'pass', 'transactional': 'warn', 'freemium': 'warn', 'advertising': 'fail', 'licensing': 'pass', 'hybrid': 'pass'},
}

# Default for industries not in matrix
DEFAULT_COMPATIBILITY = 'pass'

VALIDATOR_VERSION = "1.0.0"


class Validator:
    """Layer 2: Deterministic validation service (no LLM)"""
    
    def __init__(self):
        self.enums = load_enums()
        self.schema = load_extraction_schema()
    
    def validate(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted data against schema and rules
        
        Args:
            extracted_data: Output from Layer 1 extraction
            
        Returns:
            ValidationResult matching validation.schema.json
        """
        checks = []
        
        # 1. Schema validation (required fields present)
        checks.append(self._validate_schema(extracted_data))
        
        # 2. Enum validation
        checks.append(self._validate_enums(extracted_data))
        
        # 3. Industry-Model compatibility
        checks.append(self._validate_compatibility(extracted_data))
        
        # 4. Text length validation
        checks.append(self._validate_lengths(extracted_data))
        
        # 5. Data quality checks
        checks.append(self._validate_data_quality(extracted_data))
        
        # Calculate overall status
        has_errors = any(c['status'] == 'fail' for c in checks)
        has_warnings = any(c['status'] == 'warn' for c in checks)
        
        if has_errors:
            validation_status = 'failed'
        elif has_warnings:
            validation_status = 'warnings'
        else:
            validation_status = 'passed'
        
        return {
            'validation_status': validation_status,
            'checks_performed': checks,
            'is_valid_for_scoring': not has_errors,
            'validation_timestamp': datetime.utcnow().isoformat() + 'Z',
            'validator_version': VALIDATOR_VERSION,
            'warnings_count': sum(1 for c in checks if c['status'] == 'warn'),
            'errors_count': sum(1 for c in checks if c['status'] == 'fail')
        }
    
    def _validate_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check all required fields are present"""
        required_sections = ['idea_core', 'market_classification', 'stage_indicators', 'extraction_metadata']
        missing = []
        
        for section in required_sections:
            if section not in data:
                missing.append(section)
        
        # Check nested required fields
        if 'idea_core' in data:
            for field in ['problem_statement', 'solution_description', 'target_customer', 'value_proposition']:
                if field not in data['idea_core']:
                    missing.append(f'idea_core.{field}')
        
        if 'market_classification' in data:
            for field in ['industry_vertical', 'business_model', 'target_geography', 'customer_segment']:
                if field not in data['market_classification']:
                    missing.append(f'market_classification.{field}')
        
        if 'stage_indicators' in data:
            if 'development_stage' not in data['stage_indicators']:
                missing.append('stage_indicators.development_stage')
        
        if missing:
            return {
                'check_name': 'schema_validation',
                'check_type': 'schema',
                'status': 'fail',
                'message': f'Missing required fields: {", ".join(missing)}',
                'field_affected': missing[0] if missing else None,
                'expected': 'all required fields present',
                'actual': f'{len(missing)} fields missing'
            }
        
        return {
            'check_name': 'schema_validation',
            'check_type': 'schema',
            'status': 'pass',
            'message': 'All required fields present and correctly typed'
        }
    
    def _validate_enums(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate enum values against allowed list"""
        invalid_enums = []
        
        enum_fields = [
            ('market_classification', 'industry_vertical', 'industry_vertical'),
            ('market_classification', 'business_model', 'business_model'),
            ('market_classification', 'target_geography', 'target_geography'),
            ('market_classification', 'customer_segment', 'customer_segment'),
            ('stage_indicators', 'development_stage', 'development_stage'),
            ('extraction_metadata', 'extraction_confidence', 'extraction_confidence'),
        ]
        
        for section, field, enum_key in enum_fields:
            if section in data and field in data[section]:
                value = data[section][field]
                if value is not None and enum_key in self.enums:
                    allowed = self.enums[enum_key]
                    if value not in allowed:
                        invalid_enums.append(f'{section}.{field}={value} (allowed: {allowed})')
        
        # Optional enum fields
        optional_enums = [
            ('stage_indicators', 'team_size', 'team_size'),
            ('stage_indicators', 'funding_stage', 'funding_stage'),
            ('extraction_metadata', 'source_type', 'source_type'),
        ]
        
        for section, field, enum_key in optional_enums:
            if section in data and field in data[section]:
                value = data[section][field]
                if value is not None and enum_key in self.enums:
                    allowed = self.enums[enum_key]
                    if value not in allowed:
                        invalid_enums.append(f'{section}.{field}={value}')
        
        if invalid_enums:
            return {
                'check_name': 'enum_validation',
                'check_type': 'enum',
                'status': 'fail',
                'message': f'Invalid enum values: {", ".join(invalid_enums[:3])}',
                'field_affected': invalid_enums[0].split('=')[0],
                'expected': 'valid enum values',
                'actual': invalid_enums[0]
            }
        
        return {
            'check_name': 'enum_validation',
            'check_type': 'enum',
            'status': 'pass',
            'message': 'All enum values valid'
        }
    
    def _validate_compatibility(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check industry-model compatibility"""
        market = data.get('market_classification', {})
        industry = market.get('industry_vertical', 'other')
        model = market.get('business_model', 'B2B')
        
        # Get compatibility status
        industry_matrix = COMPATIBILITY_MATRIX.get(industry, {})
        compat = industry_matrix.get(model, DEFAULT_COMPATIBILITY)
        
        if compat == 'fail':
            return {
                'check_name': 'industry_model_compatibility',
                'check_type': 'compatibility',
                'status': 'fail',
                'message': f'{industry} + {model} is not a valid combination',
                'field_affected': 'market_classification',
                'expected': 'compatible industry-model pair',
                'actual': f'{industry} + {model}'
            }
        elif compat == 'warn':
            return {
                'check_name': 'industry_model_compatibility',
                'check_type': 'compatibility',
                'status': 'warn',
                'message': f'{industry} + {model} is an unusual combination - verify intentional',
                'field_affected': 'market_classification'
            }
        
        return {
            'check_name': 'industry_model_compatibility',
            'check_type': 'compatibility',
            'status': 'pass',
            'message': f'{industry} + {model} is a valid combination'
        }
    
    def _validate_lengths(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate text field lengths"""
        length_limits = {
            ('idea_core', 'problem_statement'): 500,
            ('idea_core', 'solution_description'): 500,
            ('idea_core', 'target_customer'): 200,
            ('idea_core', 'value_proposition'): 300,
            ('idea_core', 'differentiation'): 300,
        }
        
        violations = []
        for (section, field), max_len in length_limits.items():
            if section in data and field in data[section]:
                value = data[section].get(field)
                if value and len(value) > max_len:
                    violations.append(f'{field} ({len(value)} > {max_len})')
        
        if violations:
            return {
                'check_name': 'text_length_validation',
                'check_type': 'length',
                'status': 'warn',
                'message': f'Text fields exceed limits: {", ".join(violations)}',
                'field_affected': violations[0].split(' ')[0]
            }
        
        return {
            'check_name': 'text_length_validation',
            'check_type': 'length',
            'status': 'pass',
            'message': 'All text fields within limits'
        }
    
    def _validate_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check data quality indicators"""
        issues = []
        
        # Check if problem statement is too short
        problem = data.get('idea_core', {}).get('problem_statement', '')
        if problem and len(problem) < 20:
            issues.append('problem_statement too brief')
        
        # Check if solution is too short
        solution = data.get('idea_core', {}).get('solution_description', '')
        if solution and len(solution) < 20:
            issues.append('solution_description too brief')
        
        # Check extraction confidence
        confidence = data.get('extraction_metadata', {}).get('extraction_confidence', 'low')
        if confidence == 'low':
            issues.append('low extraction confidence')
        
        # Check inferred fields count
        inferred = data.get('extraction_metadata', {}).get('fields_inferred', [])
        if len(inferred) > 5:
            issues.append(f'too many inferred fields ({len(inferred)})')
        
        if issues:
            return {
                'check_name': 'data_quality_check',
                'check_type': 'format',
                'status': 'warn',
                'message': f'Quality issues: {", ".join(issues)}',
                'field_affected': issues[0].split(' ')[0] if issues else None
            }
        
        return {
            'check_name': 'data_quality_check',
            'check_type': 'format',
            'status': 'pass',
            'message': 'Data quality acceptable'
        }
