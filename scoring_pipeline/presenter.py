"""
Layer 4: LLM Presentation Service
Generates human-readable explanations using personas
IMPORTANT: Scores are LOCKED - LLM cannot modify them
"""

import yaml
from typing import Dict, Any, Optional
from pathlib import Path

MODULE_DIR = Path(__file__).parent


def load_personas() -> Dict[str, Any]:
    """Load persona configurations from YAML"""
    personas_path = MODULE_DIR / 'prompts' / 'personas.yaml'
    with open(personas_path, 'r') as f:
        return yaml.safe_load(f)


class Presenter:
    """Layer 4: LLM-based presentation service"""
    
    def __init__(self, gemini_client):
        """
        Initialize the presenter with a Gemini client
        
        Args:
            gemini_client: Instance of GeminiClient from services.py
        """
        self.client = gemini_client
        self.personas_config = load_personas()
        self.personas = self.personas_config.get('personas', {})
    
    def generate_presentation(
        self,
        scoring_result: Dict[str, Any],
        extracted_data: Dict[str, Any],
        persona: str = "ruthless_vc"
    ) -> Dict[str, Any]:
        """
        Generate human-readable presentation of scores
        
        Args:
            scoring_result: Output from Layer 3 scoring
            extracted_data: Output from Layer 1 extraction
            persona: Which persona to use for presentation
            
        Returns:
            Presentation result with narrative
        """
        # Get persona config
        persona_config = self.personas.get(persona, self.personas.get('ruthless_vc', {}))
        
        # Build the prompt
        system_prompt = self._build_system_prompt(persona_config)
        user_prompt = self._build_user_prompt(scoring_result, extracted_data, persona_config)
        
        # Generate the narrative
        narrative = self.client.generate_completion(
            system_prompt,
            user_prompt,
            temperature=0.7  # Some creativity allowed for presentation
        )
        
        # Format the final output
        display_name = persona_config.get('display_name', persona.replace('_', ' ').title())
        
        from datetime import datetime
        return {
            'persona': persona,
            'persona_display_name': display_name,
            'narrative': f"[AI-Generated Analysis by {display_name}]\n\n{narrative}",
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'locked_scores': {
                'final_score': scoring_result['final_score'],
                'grade': scoring_result['grade'],
                'dimension_scores': {
                    dim: data['score'] 
                    for dim, data in scoring_result['dimension_scores'].items()
                }
            }
        }
    
    def _build_system_prompt(self, persona_config: Dict) -> str:
        """Build the system prompt for the persona"""
        base_prompt = persona_config.get('system_prompt', '')
        focus_areas = persona_config.get('focus_areas', [])
        tone = persona_config.get('tone', 'professional')
        
        return f"""{base_prompt}

CRITICAL CONSTRAINTS:
1. You CANNOT modify any scores - they are locked
2. You must reference the actual dimension scores in your analysis
3. Stay in character throughout your response
4. Be specific - reference the actual data provided
5. Label your output as AI-generated

Your focus areas are:
{chr(10).join(f'- {area}' for area in focus_areas)}

Tone: {tone}"""
    
    def _build_user_prompt(
        self,
        scoring_result: Dict[str, Any],
        extracted_data: Dict[str, Any],
        persona_config: Dict
    ) -> str:
        """Build the user prompt with locked scores"""
        # Extract key info
        idea_core = extracted_data.get('idea_core', {})
        market = extracted_data.get('market_classification', {})
        stage = extracted_data.get('stage_indicators', {})
        dimension_scores = scoring_result.get('dimension_scores', {})
        
        # Format dimension scores
        scores_text = "\n".join([
            f"- {dim.replace('_', ' ').title()}: {data['score']}/100"
            for dim, data in dimension_scores.items()
        ])
        
        # Get top and bottom dimensions
        sorted_dims = sorted(
            dimension_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        top_2 = sorted_dims[:2]
        bottom_2 = sorted_dims[-2:]
        
        return f"""Analyze this startup idea and provide your perspective.

STARTUP OVERVIEW:
- Problem: {idea_core.get('problem_statement', 'Not specified')}
- Solution: {idea_core.get('solution_description', 'Not specified')}
- Target Customer: {idea_core.get('target_customer', 'Not specified')}
- Value Proposition: {idea_core.get('value_proposition', 'Not specified')}
- Differentiation: {idea_core.get('differentiation', 'Not specified')}

MARKET CONTEXT:
- Industry: {market.get('industry_vertical', 'other')}
- Business Model: {market.get('business_model', 'B2B')}
- Geography: {market.get('target_geography', 'national')}
- Customer Segment: {market.get('customer_segment', 'SMB')}

STAGE:
- Development: {stage.get('development_stage', 'concept')}
- Team Size: {stage.get('team_size', 'unknown')}
- Funding: {stage.get('funding_stage', 'unknown')}
- Has Revenue: {stage.get('has_revenue', 'unknown')}
- Has Users: {stage.get('has_users', 'unknown')}

LOCKED SCORES (you cannot modify these):
Final Score: {scoring_result['final_score']}/100 ({scoring_result['grade']})

{scores_text}

TOP STRENGTHS (highest scores):
1. {top_2[0][0].replace('_', ' ').title()}: {top_2[0][1]['score']}/100
2. {top_2[1][0].replace('_', ' ').title()}: {top_2[1][1]['score']}/100

WEAKNESSES (lowest scores):
1. {bottom_2[0][0].replace('_', ' ').title()}: {bottom_2[0][1]['score']}/100
2. {bottom_2[1][0].replace('_', ' ').title()}: {bottom_2[1][1]['score']}/100

Provide:
1. A 150-200 word analysis in your persona's voice
2. Commentary on the top 2 strengths
3. Commentary on the top 2 weaknesses
4. 3 specific, actionable next steps tied to the weak dimensions

Remember: Stay in character. Reference the actual scores. Be direct and specific."""
    
    def get_available_personas(self) -> Dict[str, Dict]:
        """Get list of available personas with their metadata"""
        return {
            name: {
                'name': config.get('name', name),
                'display_name': config.get('display_name', name),
                'icon': config.get('icon', '🎯'),
                'weight_profile': config.get('weight_profile', 'balanced'),
                'tone': config.get('tone', 'professional')
            }
            for name, config in self.personas.items()
        }
    
    def get_weight_profile_for_persona(self, persona: str) -> str:
        """Get the weight profile associated with a persona"""
        persona_config = self.personas.get(persona, {})
        return persona_config.get('weight_profile', 'balanced')
