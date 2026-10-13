"""
Scoring Pipeline Orchestrator
Coordinates all 4 layers of the deterministic scoring pipeline
"""

from typing import Dict, Any, Optional
from datetime import datetime

from .extractor import Extractor
from .validator import Validator
from .scorer import Scorer
from .presenter import Presenter


class ScoringPipeline:
    """
    Main orchestrator for the 4-layer scoring pipeline
    
    Layer 1: LLM Extraction (bounded, with schema)
    Layer 2: Deterministic Validation (pure code, no LLM)
    Layer 3: Rule-Based Scoring (no ML, no randomness)
    Layer 4: LLM Presentation (optional, scores locked)
    """
    
    PIPELINE_VERSION = "1.0.0"
    
    def __init__(self, gemini_client):
        """
        Initialize the pipeline with a Gemini client
        
        Args:
            gemini_client: Instance of GeminiClient from services.py
        """
        self.gemini_client = gemini_client
        self.extractor = Extractor(gemini_client)
        self.validator = Validator()
        self.scorer = None  # Initialized per-request with weight profile
        self.presenter = Presenter(gemini_client)
    
    def analyze(
        self,
        title: str,
        problem: str,
        solution: str,
        target_audience: str = "",
        unique_value: str = "",
        additional_context: str = "",
        source_type: str = "form_input",
        persona: str = "ruthless_vc",
        include_presentation: bool = True
    ) -> Dict[str, Any]:
        """
        Run the full scoring pipeline
        
        Args:
            title: Idea title
            problem: Problem description
            solution: Solution description
            target_audience: Target audience
            unique_value: Unique value proposition
            additional_context: Additional context (e.g., from PDF)
            source_type: Type of source input
            persona: Which persona to use for presentation
            include_presentation: Whether to run Layer 4
            
        Returns:
            Complete pipeline result
        """
        start_time = datetime.utcnow()
        
        # Layer 1: Extraction
        extraction_start = datetime.utcnow()
        extracted_data = self.extractor.extract(
            title=title,
            problem=problem,
            solution=solution,
            target_audience=target_audience,
            unique_value=unique_value,
            additional_context=additional_context,
            source_type=source_type
        )
        extraction_time = (datetime.utcnow() - extraction_start).total_seconds() * 1000
        
        # Layer 2: Validation
        validation_start = datetime.utcnow()
        validation_result = self.validator.validate(extracted_data)
        validation_time = (datetime.utcnow() - validation_start).total_seconds() * 1000
        
        # Layer 3: Scoring (even if validation has warnings)
        # Get weight profile from persona
        weight_profile = self.presenter.get_weight_profile_for_persona(persona)
        self.scorer = Scorer(weight_profile=weight_profile)
        
        scoring_start = datetime.utcnow()
        scoring_result = self.scorer.score(extracted_data)
        scoring_time = (datetime.utcnow() - scoring_start).total_seconds() * 1000
        
        # Layer 4: Presentation (optional)
        presentation_result = None
        presentation_time = 0
        
        if include_presentation:
            presentation_start = datetime.utcnow()
            presentation_result = self.presenter.generate_presentation(
                scoring_result=scoring_result,
                extracted_data=extracted_data,
                persona=persona
            )
            presentation_time = (datetime.utcnow() - presentation_start).total_seconds() * 1000
        
        total_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            'status': 'success' if validation_result['is_valid_for_scoring'] else 'validation_failed',
            'pipeline_results': {
                'extraction': {
                    'status': 'completed',
                    'data': extracted_data,
                    'confidence': extracted_data.get('extraction_metadata', {}).get('extraction_confidence', 'low'),
                    'processing_time_ms': int(extraction_time)
                },
                'validation': {
                    'status': validation_result['validation_status'],
                    'checks': validation_result['checks_performed'],
                    'is_valid_for_scoring': validation_result['is_valid_for_scoring'],
                    'validator_version': validation_result['validator_version'],
                    'warnings_count': validation_result['warnings_count'],
                    'errors_count': validation_result['errors_count']
                },
                'scoring': scoring_result,
                'presentation': presentation_result
            },
            'metadata': {
                'pipeline_version': self.PIPELINE_VERSION,
                'total_processing_time_ms': int(total_time),
                'layer_times': {
                    'extraction_ms': int(extraction_time),
                    'validation_ms': int(validation_time),
                    'scoring_ms': int(scoring_time),
                    'presentation_ms': int(presentation_time)
                },
                'processed_at': datetime.utcnow().isoformat() + 'Z',
                'persona_used': persona,
                'weight_profile_used': weight_profile
            }
        }
    
    def score_only(
        self,
        title: str,
        problem: str,
        solution: str,
        target_audience: str = "",
        unique_value: str = "",
        additional_context: str = "",
        source_type: str = "form_input",
        weight_profile: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Run extraction + validation + scoring without presentation
        Faster for cases where narrative is not needed
        """
        return self.analyze(
            title=title,
            problem=problem,
            solution=solution,
            target_audience=target_audience,
            unique_value=unique_value,
            additional_context=additional_context,
            source_type=source_type,
            persona="ruthless_vc",
            include_presentation=False
        )
    
    def get_legacy_format(self, pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert pipeline result to legacy format compatible with existing frontend
        This helps with backwards compatibility
        """
        scoring = pipeline_result['pipeline_results']['scoring']
        extraction = pipeline_result['pipeline_results']['extraction']['data']
        presentation = pipeline_result['pipeline_results'].get('presentation', {})
        
        # Map new dimension scores to old format
        dimension_scores = scoring['dimension_scores']
        
        # Derive strengths from top scoring dimensions
        sorted_dims = sorted(
            dimension_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        strengths = [
            f"Strong {dim.replace('_', ' ')}: {data['score']}/100"
            for dim, data in sorted_dims[:3]
        ]
        
        weaknesses = [
            f"Needs work on {dim.replace('_', ' ')}: {data['score']}/100"
            for dim, data in sorted_dims[-2:]
        ]
        
        return {
            'scores': {
                'problem': dimension_scores.get('problem_clarity', {}).get('score', 50),
                'solution': dimension_scores.get('solution_feasibility', {}).get('score', 50),
                'market': dimension_scores.get('market_size_potential', {}).get('score', 50),
                'moat': dimension_scores.get('competitive_landscape', {}).get('score', 50),
                'feasibility': dimension_scores.get('business_model_viability', {}).get('score', 50)
            },
            'overallScore': int(scoring['final_score']),
            'verdict': self._get_verdict(scoring['grade']),
            'strengths': strengths,
            'weaknesses': weaknesses,
            'competitors': [
                {'name': comp, 'type': 'Direct', 'reason': 'Mentioned in idea description'}
                for comp in extraction.get('idea_core', {}).get('competitors_mentioned', [])[:5]
            ],
            'leanCanvas': {
                'problemSummary': extraction.get('idea_core', {}).get('problem_statement', ''),
                'solutionSummary': extraction.get('idea_core', {}).get('solution_description', ''),
                'metrics': 'See detailed analysis',
                'channels': 'See detailed analysis',
                'revenue': extraction.get('market_classification', {}).get('business_model', 'B2B'),
                'costs': 'See detailed analysis'
            },
            'goToMarket': {
                'firstCustomers': [
                    {
                        'persona': extraction.get('idea_core', {}).get('target_customer', 'Target Customer'),
                        'details': 'Identified from idea description'
                    }
                ],
                'marketingHooks': [],
                'experiments': []
            },
            'pivotSuggestion': presentation.get('narrative', '')[:200] if presentation else '',
            # New deterministic fields
            '_deterministic': {
                'dimension_scores': scoring['dimension_scores'],
                'calculation_trace': scoring['calculation_trace'],
                'rules_version': scoring['rules_version'],
                'grade': scoring['grade'],
                'pipeline_version': pipeline_result['metadata']['pipeline_version']
            }
        }
    
    def _get_verdict(self, grade: str) -> str:
        """Convert grade to verdict text"""
        verdicts = {
            'Exceptional': 'Exceptional potential - strong investment signals',
            'Strong': 'Strong foundation with clear potential',
            'Moderate': 'Solid idea that needs refinement',
            'Weak': 'Significant concerns need addressing',
            'Critical': 'Fundamental issues - consider pivoting'
        }
        return verdicts.get(grade, 'Analysis complete')
