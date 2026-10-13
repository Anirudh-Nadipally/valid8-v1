"""
Layer 3: Rule-Based Scoring Engine
Deterministic scoring - NO ML, NO randomness
Same input ALWAYS produces same output
"""

import yaml
import re
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from datetime import datetime

MODULE_DIR = Path(__file__).parent

# Scoring constants
BASE_SCORE = 50
MIN_SCORE = 0
MAX_SCORE = 100

SCORER_VERSION = "1.0.0"


def load_scoring_rules() -> Dict[str, Any]:
    """Load scoring rules from YAML"""
    rules_path = MODULE_DIR / 'rules' / 'scoring-rules.yaml'
    with open(rules_path, 'r') as f:
        return yaml.safe_load(f)


def load_weights() -> Dict[str, Any]:
    """Load dimension weights from YAML"""
    weights_path = MODULE_DIR / 'rules' / 'weights.yaml'
    with open(weights_path, 'r') as f:
        return yaml.safe_load(f)


class Scorer:
    """Layer 3: Rule-based scoring engine (deterministic)"""
    
    def __init__(self, weight_profile: str = "balanced"):
        """
        Initialize the scorer
        
        Args:
            weight_profile: Which weight profile to use (balanced, vc_focused, indie_focused, technical_focused)
        """
        self.rules = load_scoring_rules()
        weights_config = load_weights()
        
        # Select weight profile
        profiles = weights_config.get('profiles', {})
        if weight_profile in profiles:
            self.weights = profiles[weight_profile]
        else:
            self.weights = weights_config.get('weights', profiles.get('balanced', {}))
        
        self.industry_multipliers = self.rules.get('industry_multipliers', {})
        self.grade_thresholds = self.rules.get('grade_thresholds', {
            'Exceptional': 90,
            'Strong': 75,
            'Moderate': 60,
            'Weak': 40,
            'Critical': 0
        })
    
    def score(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate scores for all dimensions
        
        Args:
            extracted_data: Validated output from Layer 1/2
            
        Returns:
            ScoringResult matching score.schema.json
        """
        dimension_scores = {}
        calculation_trace = []
        
        # Score each dimension
        dimensions = [
            'problem_clarity',
            'solution_feasibility',
            'market_size_potential',
            'competitive_landscape',
            'business_model_viability',
            'team_readiness',
            'data_completeness'
        ]
        
        for dimension in dimensions:
            score, traces = self._score_dimension(dimension, extracted_data)
            
            # Apply industry multiplier for market dimension
            if dimension == 'market_size_potential':
                industry = extracted_data.get('market_classification', {}).get('industry_vertical', 'other')
                multiplier = self.industry_multipliers.get(industry, 1.0)
                score = int(score * multiplier)
            
            # Clamp to valid range
            score = max(MIN_SCORE, min(MAX_SCORE, score))
            
            # Get weight for this dimension
            weight = self.weights.get(dimension, 0.1)
            
            # Store dimension score
            dimension_scores[dimension] = {
                'score': score,
                'weight': weight,
                'weighted_score': round(score * weight, 2),
                'rules_triggered': [t['rule_id'] for t in traces if t['applied']]
            }
            
            # Add to calculation trace
            calculation_trace.extend(traces)
        
        # Calculate final weighted score
        final_score = sum(d['weighted_score'] for d in dimension_scores.values())
        
        # Determine grade
        grade = self._get_grade(final_score)
        
        return {
            'final_score': round(final_score, 2),
            'grade': grade,
            'dimension_scores': dimension_scores,
            'calculation_trace': calculation_trace,
            'rules_version': self.rules.get('version', SCORER_VERSION),
            'scored_at': datetime.utcnow().isoformat() + 'Z',
            'scoring_metadata': {
                'rules_applied_count': len(calculation_trace),
                'rules_triggered_count': sum(1 for t in calculation_trace if t['applied']),
                'industry_multiplier_used': self.industry_multipliers.get(
                    extracted_data.get('market_classification', {}).get('industry_vertical', 'other'),
                    1.0
                ),
                'weight_profile': 'balanced'
            }
        }
    
    def _score_dimension(self, dimension: str, data: Dict[str, Any]) -> Tuple[int, List[Dict]]:
        """
        Score a single dimension by evaluating all its rules
        
        Returns:
            Tuple of (score, list of trace entries)
        """
        base_score = BASE_SCORE
        traces = []
        
        # Get rules for this dimension
        dimension_rules = self.rules.get(dimension, {}).get('rules', [])
        
        for rule in dimension_rules:
            applies, reason = self._evaluate_rule(rule, data)
            points = rule.get('points', 0) if applies else 0
            
            traces.append({
                'rule_id': rule['id'],
                'dimension': dimension,
                'applied': applies,
                'points': points,
                'condition': rule.get('condition', ''),
                'reason': reason
            })
            
            if applies:
                base_score += points
        
        return base_score, traces
    
    def _evaluate_rule(self, rule: Dict[str, Any], data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Evaluate a single rule against the data
        
        Returns:
            Tuple of (applies: bool, reason: str)
        """
        rule_id = rule.get('id', '')
        condition = rule.get('condition', '')
        
        # Parse the condition and evaluate
        try:
            # Problem Clarity rules
            if rule_id.startswith('PC-'):
                return self._eval_problem_clarity_rule(rule, data)
            
            # Solution Feasibility rules
            elif rule_id.startswith('SF-'):
                return self._eval_solution_feasibility_rule(rule, data)
            
            # Market Size rules
            elif rule_id.startswith('MS-'):
                return self._eval_market_size_rule(rule, data)
            
            # Competitive Landscape rules
            elif rule_id.startswith('CL-'):
                return self._eval_competitive_landscape_rule(rule, data)
            
            # Business Model rules
            elif rule_id.startswith('BM-'):
                return self._eval_business_model_rule(rule, data)
            
            # Team Readiness rules
            elif rule_id.startswith('TR-'):
                return self._eval_team_readiness_rule(rule, data)
            
            # Data Completeness rules
            elif rule_id.startswith('DC-'):
                return self._eval_data_completeness_rule(rule, data)
            
            else:
                return False, f"Unknown rule type: {rule_id}"
                
        except Exception as e:
            return False, f"Error evaluating rule: {str(e)}"
    
    def _eval_problem_clarity_rule(self, rule: Dict, data: Dict) -> Tuple[bool, str]:
        """Evaluate Problem Clarity dimension rules"""
        rule_id = rule['id']
        problem = data.get('idea_core', {}).get('problem_statement', '') or ''
        keywords = rule.get('keywords', [])
        
        if rule_id == 'PC-001':
            # problem_statement.length > 100
            applies = len(problem) > 100
            return applies, f"Problem statement is {len(problem)} characters"
        
        elif rule_id == 'PC-002':
            # Contains numbers or metrics
            pattern = r'\b(\d+|%|\$|million|billion|hours|days|x|times)\b'
            applies = bool(re.search(pattern, problem, re.IGNORECASE))
            return applies, "Contains quantifiable metrics" if applies else "No quantifiable metrics found"
        
        elif rule_id == 'PC-003':
            # Mentions specific pain point
            applies = any(kw.lower() in problem.lower() for kw in keywords)
            matched = [kw for kw in keywords if kw.lower() in problem.lower()]
            return applies, f"Contains pain keyword: {matched[0]}" if matched else "No pain keywords found"
        
        elif rule_id == 'PC-004':
            # competitors_mentioned is not empty OR differentiation is not null
            competitors = data.get('idea_core', {}).get('competitors_mentioned', []) or []
            diff = data.get('idea_core', {}).get('differentiation')
            applies = len(competitors) > 0 or diff is not None
            return applies, "Competitive awareness shown" if applies else "No competitive context"
        
        elif rule_id == 'PC-005':
            # problem_statement in fields_extracted
            extracted = data.get('extraction_metadata', {}).get('fields_extracted', []) or []
            applies = 'problem_statement' in extracted
            return applies, "Problem directly extracted" if applies else "Problem was inferred"
        
        elif rule_id == 'PC-006':
            # problem_statement.length < 50
            applies = len(problem) < 50 and len(problem) > 0
            return applies, f"Problem description too brief ({len(problem)} chars)" if applies else "Adequate length"
        
        elif rule_id == 'PC-007':
            # Contains vague language
            applies = any(kw.lower() in problem.lower() for kw in keywords)
            return applies, "Contains vague language" if applies else "No vague language detected"
        
        return False, f"Unknown rule: {rule_id}"
    
    def _eval_solution_feasibility_rule(self, rule: Dict, data: Dict) -> Tuple[bool, str]:
        """Evaluate Solution Feasibility dimension rules"""
        rule_id = rule['id']
        solution = data.get('idea_core', {}).get('solution_description', '') or ''
        stage = data.get('stage_indicators', {}).get('development_stage', 'concept')
        industry = data.get('market_classification', {}).get('industry_vertical', 'other')
        has_users = data.get('stage_indicators', {}).get('has_users', False)
        keywords = rule.get('keywords', [])
        
        if rule_id == 'SF-001':
            applies = len(solution) > 100
            return applies, f"Solution description is {len(solution)} characters"
        
        elif rule_id == 'SF-002':
            applies = any(kw.lower() in solution.lower() for kw in keywords)
            matched = [kw for kw in keywords if kw.lower() in solution.lower()]
            return applies, f"Technology mentioned: {matched[0] if matched else 'none'}"
        
        elif rule_id == 'SF-003':
            applies = stage in ['MVP', 'early_traction', 'growth', 'scale']
            return applies, f"Development stage: {stage}"
        
        elif rule_id == 'SF-004':
            applies = stage == 'prototype'
            return applies, f"At prototype stage" if applies else f"Stage is {stage}"
        
        elif rule_id == 'SF-005':
            applies = stage == 'concept'
            return applies, "At concept stage only" if applies else f"Stage is {stage}"
        
        elif rule_id == 'SF-006':
            applies = has_users == True
            return applies, "Has actual users" if applies else "No users yet"
        
        elif rule_id == 'SF-007':
            applies = industry == 'deeptech' and stage == 'concept'
            return applies, "DeepTech at concept stage (high risk)" if applies else "Not applicable"
        
        return False, f"Unknown rule: {rule_id}"
    
    def _eval_market_size_rule(self, rule: Dict, data: Dict) -> Tuple[bool, str]:
        """Evaluate Market Size Potential dimension rules"""
        rule_id = rule['id']
        market = data.get('market_classification', {})
        geography = market.get('target_geography', 'national')
        segment = market.get('customer_segment', 'SMB')
        model = market.get('business_model', 'B2B')
        
        geography_rules = {
            'MS-001': ('global', 'Global market target'),
            'MS-002': ('multi_national', 'Multi-national market target'),
            'MS-003': ('national', 'National market target'),
            'MS-004': ('regional', 'Regional market target'),
            'MS-005': ('local', 'Local market target'),
        }
        
        if rule_id in geography_rules:
            expected, msg = geography_rules[rule_id]
            applies = geography == expected
            return applies, msg if applies else f"Geography is {geography}"
        
        segment_rules = {
            'MS-006': ('enterprise', 'Enterprise customer segment'),
            'MS-007': ('mid_market', 'Mid-market customer segment'),
            'MS-008': ('SMB', 'SMB customer segment'),
        }
        
        if rule_id in segment_rules:
            expected, msg = segment_rules[rule_id]
            applies = segment == expected
            return applies, msg if applies else f"Segment is {segment}"
        
        if rule_id == 'MS-009':
            applies = segment == 'consumer' and geography in ['global', 'multi_national']
            return applies, "Consumer at scale" if applies else "Not consumer at scale"
        
        if rule_id == 'MS-010':
            applies = model in ['SaaS', 'marketplace']
            return applies, f"Scalable model ({model})" if applies else f"Model is {model}"
        
        return False, f"Unknown rule: {rule_id}"
    
    def _eval_competitive_landscape_rule(self, rule: Dict, data: Dict) -> Tuple[bool, str]:
        """Evaluate Competitive Landscape dimension rules"""
        rule_id = rule['id']
        idea_core = data.get('idea_core', {})
        market = data.get('market_classification', {})
        competitors = idea_core.get('competitors_mentioned', []) or []
        diff = idea_core.get('differentiation', '') or ''
        industry = market.get('industry_vertical', 'other')
        model = market.get('business_model', 'B2B')
        segment = market.get('customer_segment', 'SMB')
        keywords = rule.get('keywords', [])
        
        if rule_id == 'CL-001':
            applies = len(competitors) > 0
            return applies, f"Competitors identified: {', '.join(competitors[:3])}" if applies else "No competitors mentioned"
        
        elif rule_id == 'CL-002':
            applies = diff is not None and len(diff) > 50
            return applies, "Clear differentiation described" if applies else "Differentiation unclear"
        
        elif rule_id == 'CL-003':
            applies = industry in ['ai_ml', 'climate', 'deeptech']
            return applies, f"Emerging industry: {industry}" if applies else f"Industry: {industry}"
        
        elif rule_id == 'CL-004':
            applies = industry in ['e_commerce', 'social', 'consumer_app']
            return applies, f"Saturated industry: {industry}" if applies else "Not in saturated industry"
        
        elif rule_id == 'CL-005':
            applies = any(kw.lower() in diff.lower() for kw in keywords)
            return applies, "Unique IP/tech mentioned" if applies else "No unique tech claims"
        
        elif rule_id == 'CL-006':
            applies = len(competitors) == 0 and (diff is None or diff == '')
            return applies, "No competitive awareness" if applies else "Has competitive context"
        
        elif rule_id == 'CL-007':
            applies = model == 'marketplace' and segment == 'consumer'
            return applies, "Consumer marketplace (winner-take-all risk)" if applies else "Not consumer marketplace"
        
        return False, f"Unknown rule: {rule_id}"
    
    def _eval_business_model_rule(self, rule: Dict, data: Dict) -> Tuple[bool, str]:
        """Evaluate Business Model Viability dimension rules"""
        rule_id = rule['id']
        market = data.get('market_classification', {})
        stage = data.get('stage_indicators', {})
        model = market.get('business_model', 'B2B')
        segment = market.get('customer_segment', 'SMB')
        has_revenue = stage.get('has_revenue', False)
        
        model_rules = {
            'BM-001': (['SaaS', 'subscription'], 'Recurring revenue model'),
            'BM-002': (['marketplace'], 'Platform/marketplace model'),
            'BM-003': (['B2B'], 'B2B sales model'),
            'BM-004': (['transactional'], 'Transactional revenue model'),
            'BM-005': (['advertising'], 'Ad-supported model'),
        }
        
        for rid, (models, msg) in model_rules.items():
            if rule_id == rid:
                applies = model in models
                return applies, msg if applies else f"Model is {model}"
        
        if rule_id == 'BM-006':
            applies = model == 'freemium' and segment in ['consumer', 'prosumer']
            return applies, "Freemium consumer model" if applies else "Not freemium consumer"
        
        elif rule_id == 'BM-007':
            applies = has_revenue == True
            return applies, "Already generating revenue" if applies else "No revenue yet"
        
        elif rule_id == 'BM-008':
            applies = segment == 'enterprise' and model == 'B2B'
            return applies, "Enterprise B2B (high value)" if applies else "Not enterprise B2B"
        
        return False, f"Unknown rule: {rule_id}"
    
    def _eval_team_readiness_rule(self, rule: Dict, data: Dict) -> Tuple[bool, str]:
        """Evaluate Team Readiness dimension rules"""
        rule_id = rule['id']
        stage_data = data.get('stage_indicators', {})
        team_size = stage_data.get('team_size')
        funding = stage_data.get('funding_stage')
        dev_stage = stage_data.get('development_stage', 'concept')
        has_revenue = stage_data.get('has_revenue', False)
        
        if rule_id == 'TR-001':
            applies = team_size in ['6-20', '21-50', '50+']
            return applies, f"Established team: {team_size}" if applies else f"Team size: {team_size}"
        
        elif rule_id == 'TR-002':
            applies = team_size == '2-5'
            return applies, "Small team (typical early stage)" if applies else f"Team size: {team_size}"
        
        elif rule_id == 'TR-003':
            applies = team_size == 'solo'
            return applies, "Solo founder" if applies else f"Team size: {team_size}"
        
        elif rule_id == 'TR-004':
            applies = team_size is None
            return applies, "Team size not specified" if applies else f"Team size: {team_size}"
        
        elif rule_id == 'TR-005':
            applies = funding in ['series_a', 'series_b_plus']
            return applies, f"Institutional funding: {funding}" if applies else f"Funding: {funding}"
        
        elif rule_id == 'TR-006':
            applies = funding == 'seed'
            return applies, "Seed funding received" if applies else f"Funding: {funding}"
        
        elif rule_id == 'TR-007':
            applies = funding == 'pre_seed'
            return applies, "Pre-seed funding" if applies else f"Funding: {funding}"
        
        elif rule_id == 'TR-008':
            applies = funding == 'bootstrapped' and has_revenue == True
            return applies, "Profitable bootstrap" if applies else "Not profitable bootstrap"
        
        elif rule_id == 'TR-009':
            applies = dev_stage in ['growth', 'scale'] and team_size == 'solo'
            return applies, "Growth stage with solo founder (risk)" if applies else "Team appropriate for stage"
        
        return False, f"Unknown rule: {rule_id}"
    
    def _eval_data_completeness_rule(self, rule: Dict, data: Dict) -> Tuple[bool, str]:
        """Evaluate Data Completeness dimension rules"""
        rule_id = rule['id']
        meta = data.get('extraction_metadata', {})
        stage = data.get('stage_indicators', {})
        confidence = meta.get('extraction_confidence', 'low')
        source_type = meta.get('source_type', 'form_input')
        fields_inferred = meta.get('fields_inferred', []) or []
        
        if rule_id == 'DC-001':
            # Check all required fields are non-null
            required = [
                data.get('idea_core', {}).get('problem_statement'),
                data.get('idea_core', {}).get('solution_description'),
                data.get('idea_core', {}).get('target_customer'),
                data.get('idea_core', {}).get('value_proposition'),
                data.get('market_classification', {}).get('industry_vertical'),
                data.get('market_classification', {}).get('business_model'),
                data.get('market_classification', {}).get('target_geography'),
                data.get('market_classification', {}).get('customer_segment'),
                stage.get('development_stage'),
            ]
            applies = all(f is not None and f != '' for f in required)
            return applies, "All required fields populated" if applies else "Some required fields missing"
        
        elif rule_id == 'DC-002':
            applies = confidence == 'high'
            return applies, "High extraction confidence" if applies else f"Confidence: {confidence}"
        
        elif rule_id == 'DC-003':
            applies = confidence == 'medium'
            return applies, "Medium extraction confidence" if applies else f"Confidence: {confidence}"
        
        elif rule_id == 'DC-004':
            applies = confidence == 'low'
            return applies, "Low extraction confidence" if applies else f"Confidence: {confidence}"
        
        elif rule_id == 'DC-005':
            applies = source_type in ['pitch_deck', 'business_plan', 'interview_transcript']
            return applies, f"Rich source: {source_type}" if applies else f"Source: {source_type}"
        
        elif rule_id == 'DC-006':
            applies = source_type == 'form_input'
            return applies, "Form-based input" if applies else f"Source: {source_type}"
        
        elif rule_id == 'DC-007':
            applies = len(fields_inferred) > 3
            return applies, f"Too many inferred fields ({len(fields_inferred)})" if applies else f"Inferred: {len(fields_inferred)}"
        
        elif rule_id == 'DC-008':
            applies = len(fields_inferred) == 0
            return applies, "No fields inferred" if applies else f"Inferred: {len(fields_inferred)}"
        
        elif rule_id == 'DC-009':
            # Count optional fields that are populated
            optional_fields = [
                stage.get('team_size'),
                stage.get('funding_stage'),
                stage.get('has_revenue'),
                stage.get('has_users'),
            ]
            populated = sum(1 for f in optional_fields if f is not None)
            applies = populated > 0
            return applies, f"Optional context provided ({populated}/4)" if applies else "No optional fields"
        
        return False, f"Unknown rule: {rule_id}"
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to grade"""
        if score >= self.grade_thresholds.get('Exceptional', 90):
            return 'Exceptional'
        elif score >= self.grade_thresholds.get('Strong', 75):
            return 'Strong'
        elif score >= self.grade_thresholds.get('Moderate', 60):
            return 'Moderate'
        elif score >= self.grade_thresholds.get('Weak', 40):
            return 'Weak'
        else:
            return 'Critical'
