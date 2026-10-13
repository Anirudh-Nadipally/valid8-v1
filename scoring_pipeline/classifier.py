"""
Layer: Deterministic Pattern Classification
NO LLM, NO randomness - Pure function
Same input ALWAYS produces same output

This is the core of Valid8 Pro v4's consistency guarantee.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from .archetypes import (
    ARCHETYPES, NEEDS_MORE_DATA, Archetype, Tier,
    get_archetype, get_conviction_display
)


@dataclass
class ClassificationResult:
    """Result of pattern classification"""
    archetype_id: str
    archetype_name: str
    icon: str
    tagline: str
    tier: int
    conviction: int  # 1-4
    conviction_dots: str
    conviction_label: str
    glow_color: str
    reasons: List[str]
    action_focus: str
    description: str


def classify_archetype(signals: Dict[str, Any]) -> ClassificationResult:
    """
    Deterministic pattern classification - NO LLM
    
    Args:
        signals: Dictionary containing extracted signal values
            - problem: str (e.g., "quantified_pain", "vague_pain")
            - solution: str (e.g., "shipping", "buildable", "concept")
            - customer: str (e.g., "specific", "generic", "unclear")
            - market: str (e.g., "massive", "large", "niche")
            - team: str (e.g., "established", "solo", "none")
            - model: str (e.g., "scalable", "proven", "unclear")
            - competition: str (e.g., "validated", "saturated", "none")
            - differentiation: str (e.g., "clear", "strong", "weak")
            - urgency: str (e.g., "high", "medium", "low")
            - feasibility: str (e.g., "proven", "unproven", "breakthrough_required")
            - revenue: str (e.g., "has_revenue", "pre_revenue", "none")
            - scale: str (e.g., "global", "regional", "local")
            
    Returns:
        ClassificationResult with archetype, conviction, and reasons
    """
    # Normalize signals to lowercase
    normalized = {k: str(v).lower() if v else "" for k, v in signals.items()}
    
    # Track match reasons
    reasons: List[str] = []
    conviction_factors: List[bool] = []
    
    # Check archetypes in priority order (Tier 1 first, then 2, then 3)
    for archetype_id in [
        # Tier 1: High Conviction
        "painkiller", "rocket", "execution_play",
        # Tier 2: Conditional  
        "vitamin", "moonshot", "lifestyle",
        # Tier 3: Warning
        "solution_seeking_problem", "red_ocean"
    ]:
        archetype = ARCHETYPES[archetype_id]
        match_result = _check_archetype_match(normalized, archetype)
        
        if match_result["matches"]:
            conviction = _calculate_conviction(normalized, archetype, match_result)
            conviction_display = get_conviction_display(conviction)
            
            return ClassificationResult(
                archetype_id=archetype.id,
                archetype_name=archetype.name,
                icon=archetype.icon,
                tagline=archetype.tagline,
                tier=archetype.tier.value,
                conviction=conviction,
                conviction_dots=conviction_display["dots"],
                conviction_label=conviction_display["label"],
                glow_color=archetype.glow_color,
                reasons=match_result["reasons"],
                action_focus=archetype.action_focus,
                description=archetype.description
            )
    
    # No match - return "needs more data"
    conviction_display = get_conviction_display(1)
    return ClassificationResult(
        archetype_id=NEEDS_MORE_DATA.id,
        archetype_name=NEEDS_MORE_DATA.name,
        icon=NEEDS_MORE_DATA.icon,
        tagline=NEEDS_MORE_DATA.tagline,
        tier=NEEDS_MORE_DATA.tier.value,
        conviction=1,
        conviction_dots=conviction_display["dots"],
        conviction_label=conviction_display["label"],
        glow_color=NEEDS_MORE_DATA.glow_color,
        reasons=["Insufficient signal data for classification"],
        action_focus=NEEDS_MORE_DATA.action_focus,
        description=NEEDS_MORE_DATA.description
    )


def _check_archetype_match(signals: Dict[str, str], archetype: Archetype) -> Dict[str, Any]:
    """
    Check if signals match an archetype's criteria
    
    Returns dict with:
        - matches: bool
        - reasons: List[str] explaining why it matched
        - match_score: float (0-1) for partial matches
    """
    if not archetype.criteria:
        return {"matches": False, "reasons": [], "match_score": 0}
    
    matched_criteria = 0
    total_criteria = len(archetype.criteria)
    reasons = []
    
    for dimension, valid_values in archetype.criteria.items():
        signal_value = signals.get(dimension, "")
        
        # Check if signal value matches any of the valid values
        if any(valid.lower() in signal_value for valid in valid_values):
            matched_criteria += 1
            reasons.append(f"{dimension.replace('_', ' ').title()}: {signal_value}")
    
    # Require majority of criteria to match
    match_threshold = total_criteria * 0.6  # 60% threshold
    matches = matched_criteria >= match_threshold
    
    return {
        "matches": matches,
        "reasons": reasons,
        "match_score": matched_criteria / total_criteria if total_criteria > 0 else 0
    }


def _calculate_conviction(signals: Dict[str, str], archetype: Archetype, match_result: Dict) -> int:
    """
    Calculate conviction level (1-4) based on signal strength
    
    Factors:
    - Match score (how many criteria matched)
    - Data completeness
    - Tier bonuses
    """
    base_conviction = 2  # Start at moderate
    
    # Factor 1: Match score
    match_score = match_result.get("match_score", 0)
    if match_score >= 1.0:
        base_conviction += 1
    elif match_score >= 0.8:
        base_conviction += 0.5
    
    # Factor 2: Data completeness
    filled_signals = sum(1 for v in signals.values() if v and v != "unclear" and v != "none")
    total_signals = len(signals)
    completeness = filled_signals / max(total_signals, 1)
    
    if completeness >= 0.8:
        base_conviction += 0.5
    elif completeness < 0.5:
        base_conviction -= 0.5
    
    # Factor 3: Tier bonus (Tier 1 archetypes get slight boost when matched well)
    if archetype.tier == Tier.HIGH_CONVICTION and match_score >= 0.8:
        base_conviction += 0.5
    
    # Factor 4: Revenue indicator (strong positive signal)
    if signals.get("revenue") in ["has_revenue", "profitable"]:
        base_conviction += 0.5
    
    # Clamp to 1-4 range
    return max(1, min(4, round(base_conviction)))


def extract_signals_from_extracted_data(extracted_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Transform Layer 1/2 extracted data into signals for classification
    
    Maps the complex extracted structure to simple signal strings
    """
    signals = {}
    
    # Problem clarity signal
    problem_data = extracted_data.get("problem", {})
    if isinstance(problem_data, dict):
        severity = problem_data.get("severity", "")
        frequency = problem_data.get("frequency", "")
        quantified = problem_data.get("quantified", False)
        
        if quantified or severity in ["critical", "high"]:
            signals["problem"] = "quantified_pain"
        elif severity == "medium" or frequency in ["daily", "weekly"]:
            signals["problem"] = "clear_pain"
        else:
            signals["problem"] = "vague_pain"
        
        # Urgency
        signals["urgency"] = "high" if severity in ["critical", "high"] else "low"
    else:
        signals["problem"] = str(problem_data) if problem_data else "unclear"
    
    # Solution signal
    solution_data = extracted_data.get("solution", {})
    if isinstance(solution_data, dict):
        stage = solution_data.get("stage", "")
        feasibility = solution_data.get("technical_feasibility", "")
        
        if stage in ["launched", "live", "shipping"]:
            signals["solution"] = "shipping"
        elif stage in ["mvp", "prototype", "beta"]:
            signals["solution"] = "buildable"
        elif feasibility in ["proven", "achievable"]:
            signals["solution"] = "buildable"
        else:
            signals["solution"] = "concept"
        
        signals["feasibility"] = feasibility if feasibility else "unproven"
    else:
        signals["solution"] = str(solution_data) if solution_data else "unclear"
    
    # Customer/audience signal
    audience = extracted_data.get("target_audience", "") or extracted_data.get("customer", "")
    if isinstance(audience, dict):
        specificity = audience.get("specificity", "")
        signals["customer"] = specificity if specificity else "generic"
    elif audience and len(str(audience)) > 20:  # Detailed description
        signals["customer"] = "specific"
    else:
        signals["customer"] = "generic"
    
    # Market signal
    market_data = extracted_data.get("market", {})
    if isinstance(market_data, dict):
        tam = market_data.get("tam", 0)
        if isinstance(tam, str):
            # Parse "$47B" or "47 billion"
            tam = _parse_market_size(tam)
        
        if tam >= 10_000_000_000:  # $10B+
            signals["market"] = "massive"
        elif tam >= 1_000_000_000:  # $1B+
            signals["market"] = "large"
        elif tam >= 100_000_000:  # $100M+
            signals["market"] = "medium"
        else:
            signals["market"] = "niche"
    else:
        signals["market"] = "unclear"
    
    # Team signal
    team_data = extracted_data.get("team", {})
    if isinstance(team_data, dict):
        size = team_data.get("size", 1)
        experience = team_data.get("relevant_experience", False)
        
        if size >= 3 and experience:
            signals["team"] = "established"
        elif size >= 2:
            signals["team"] = "small"
        else:
            signals["team"] = "solo"
    else:
        signals["team"] = "solo"
    
    # Competition signal
    competitors = extracted_data.get("competitors", [])
    if competitors:
        has_funded = any(
            c.get("funding") or c.get("raised") 
            for c in competitors if isinstance(c, dict)
        )
        
        if len(competitors) > 5:
            signals["competition"] = "saturated"
        elif has_funded:
            signals["competition"] = "validated"
        else:
            signals["competition"] = "emerging"
    else:
        signals["competition"] = "none"
    
    # Differentiation signal
    moat = extracted_data.get("moat", "") or extracted_data.get("unique_value", "")
    if moat and len(str(moat)) > 30:  # Detailed moat
        signals["differentiation"] = "clear"
    elif moat:
        signals["differentiation"] = "moderate"
    else:
        signals["differentiation"] = "weak"
    
    # Revenue signal
    revenue = extracted_data.get("revenue", {})
    if isinstance(revenue, dict):
        if revenue.get("has_revenue") or revenue.get("mrr", 0) > 0:
            signals["revenue"] = "has_revenue"
        else:
            signals["revenue"] = "pre_revenue"
    else:
        signals["revenue"] = "none"
    
    # Scale signal
    geography = extracted_data.get("geography", "")
    if "global" in str(geography).lower():
        signals["scale"] = "global"
    elif any(word in str(geography).lower() for word in ["national", "country", "india", "us", "uk"]):
        signals["scale"] = "regional"
    else:
        signals["scale"] = "local"
    
    # Business model signal
    model = extracted_data.get("business_model", "")
    if any(word in str(model).lower() for word in ["saas", "subscription", "marketplace", "platform"]):
        signals["model"] = "scalable"
    elif any(word in str(model).lower() for word in ["freemium", "transaction"]):
        signals["model"] = "proven"
    else:
        signals["model"] = "unclear"
    
    return signals


def _parse_market_size(value: str) -> int:
    """Parse market size strings like '$47B' or '47 billion' to integers"""
    import re
    
    value = value.lower().replace("$", "").replace(",", "").strip()
    
    # Match number with multiplier (B, M, K)
    match = re.search(r'([\d.]+)\s*(billion|b|million|m|thousand|k)?', value)
    if match:
        num = float(match.group(1))
        multiplier = match.group(2) or ""
        
        if multiplier.startswith('b'):
            return int(num * 1_000_000_000)
        elif multiplier.startswith('m'):
            return int(num * 1_000_000)
        elif multiplier.startswith('k'):
            return int(num * 1_000)
        else:
            return int(num)
    
    return 0


# Convenience function for quick classification from raw input
def quick_classify(
    problem: str = "",
    solution: str = "",
    customer: str = "",
    market: str = "",
    competition: str = "",
    differentiation: str = ""
) -> ClassificationResult:
    """
    Quick classification with simple string inputs
    Useful for testing or simple API calls
    """
    signals = {
        "problem": problem,
        "solution": solution,
        "customer": customer,
        "market": market,
        "competition": competition,
        "differentiation": differentiation,
    }
    return classify_archetype(signals)
