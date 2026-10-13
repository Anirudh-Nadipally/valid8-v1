"""
Archetype Definitions for Valid8 Pro v4
8 Startup Archetypes that replace numerical scoring
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class Tier(Enum):
    """Archetype tiers - higher priority archetypes are checked first"""
    HIGH_CONVICTION = 1    # Painkiller, Rocket, Execution Play
    CONDITIONAL = 2        # Vitamin, Moonshot, Lifestyle
    WARNING = 3            # Solution Seeking, Red Ocean


@dataclass
class Archetype:
    """Defines a startup archetype with classification criteria"""
    id: str
    name: str
    icon: str
    tagline: str
    tier: Tier
    glow_color: str  # CSS class for tier-based styling
    criteria: Dict[str, List[str]]  # Required signal values to match
    description: str
    action_focus: str  # What the founder should focus on


# =============================================================================
# THE 8 ARCHETYPES (Priority Order)
# =============================================================================

ARCHETYPES: Dict[str, Archetype] = {
    # TIER 1: High Conviction (Green Glow)
    "painkiller": Archetype(
        id="painkiller",
        name="Painkiller",
        icon="🔥",
        tagline="Solving urgent, quantified pain with a clear solution.",
        tier=Tier.HIGH_CONVICTION,
        glow_color="emerald",
        criteria={
            "problem": ["quantified_pain", "urgent_pain"],
            "solution": ["shipping", "buildable"],
            "customer": ["specific", "reachable"]
        },
        description="You're solving a severe, measurable problem for a well-defined customer. This is the strongest foundation for a startup.",
        action_focus="Double down on customer development. Get 10 paying customers ASAP."
    ),
    
    "rocket": Archetype(
        id="rocket",
        name="Rocket",
        icon="🚀",
        tagline="Big market opportunity with strong execution team.",
        tier=Tier.HIGH_CONVICTION,
        glow_color="emerald",
        criteria={
            "market": ["massive", "large"],
            "team": ["established", "experienced"],
            "model": ["scalable", "proven"]
        },
        description="You have the market size and team composition that VCs look for. Focus on proving unit economics.",
        action_focus="Prove your CAC:LTV ratio. Show you can acquire customers profitably at scale."
    ),
    
    "execution_play": Archetype(
        id="execution_play",
        name="Execution Play",
        icon="🔷",
        tagline="Proven market. Win by out-executing.",
        tier=Tier.HIGH_CONVICTION,
        glow_color="emerald",
        criteria={
            "competition": ["validated", "established"],
            "differentiation": ["clear", "strong"]
        },
        description="Your idea targets a validated market (competitors exist and are funded). Success depends on execution quality, not market validation.",
        action_focus="Find your wedge, move fast, out-execute. Study competitor weaknesses."
    ),
    
    # TIER 2: Conditional (Amber Glow)
    "vitamin": Archetype(
        id="vitamin",
        name="Vitamin",
        icon="💊",
        tagline="Nice to have. Find the urgency.",
        tier=Tier.CONDITIONAL,
        glow_color="amber",
        criteria={
            "problem": ["vague_pain", "nice_to_have"],
            "urgency": ["low", "none"]
        },
        description="Your solution is helpful but not essential. Customers may delay or skip purchasing without immediate consequences.",
        action_focus="Find the hair-on-fire moment. When does this become urgent? Reposition around that trigger."
    ),
    
    "moonshot": Archetype(
        id="moonshot",
        name="Moonshot",
        icon="🌙",
        tagline="Huge if it works. High risk, high reward.",
        tier=Tier.CONDITIONAL,
        glow_color="amber",
        criteria={
            "market": ["massive", "large"],
            "feasibility": ["unproven", "breakthrough_required"]
        },
        description="You're attempting something with massive potential but significant technical or market risk.",
        action_focus="De-risk the biggest unknown first. Find a small proof that the core thesis works."
    ),
    
    "lifestyle": Archetype(
        id="lifestyle",
        name="Lifestyle",
        icon="🏝️",
        tagline="Profitable, not venture scale.",
        tier=Tier.CONDITIONAL,
        glow_color="amber",
        criteria={
            "market": ["niche", "limited"],
            "revenue": ["has_revenue", "profitable"],
            "scale": ["limited", "local"]
        },
        description="This can be a great business but likely won't 10x. Perfect for bootstrapping, wrong for VC.",
        action_focus="Optimize for profitability and lifestyle. Don't chase venture scale if the market doesn't support it."
    ),
    
    # TIER 3: Warning (Red Glow)
    "solution_seeking_problem": Archetype(
        id="solution_seeking_problem",
        name="Solution Seeking Problem",
        icon="🔍",
        tagline="Cool tech looking for users.",
        tier=Tier.WARNING,
        glow_color="rose",
        criteria={
            "solution": ["detailed", "advanced"],
            "problem": ["vague_pain", "unclear"],
            "customer": ["generic", "unclear"]
        },
        description="You have a sophisticated solution but haven't found a customer with a burning problem. Tech-first, customer-second.",
        action_focus="Stop building. Talk to 50 potential users this week. Find the pain before the solution."
    ),
    
    "red_ocean": Archetype(
        id="red_ocean",
        name="Red Ocean",
        icon="⚠️",
        tagline="Crowded market, unclear differentiation.",
        tier=Tier.WARNING,
        glow_color="rose",
        criteria={
            "competition": ["saturated", "crowded"],
            "differentiation": ["weak", "unclear"]
        },
        description="You're entering a crowded space without a clear advantage. Competing on features or price rarely works.",
        action_focus="Find a 10x wedge or pivot. What can you do 10x better than everyone else? If nothing, reconsider."
    ),
}

# Default fallback when no pattern matches
NEEDS_MORE_DATA = Archetype(
    id="needs_more_data",
    name="Needs More Data",
    icon="❓",
    tagline="Not enough information to classify.",
    tier=Tier.WARNING,
    glow_color="slate",
    criteria={},
    description="We couldn't confidently classify your idea. Add more detail about your problem, solution, or market.",
    action_focus="Provide more context about your target customer, the problem severity, and your unique approach."
)


# =============================================================================
# CONVICTION LEVELS
# =============================================================================

CONVICTION_LEVELS = {
    4: {"dots": "●●●●", "label": "Exceptional", "description": "All signals align strongly"},
    3: {"dots": "●●●○", "label": "Strong", "description": "Most signals are positive"},
    2: {"dots": "●●○○", "label": "Moderate", "description": "Mixed signals, some gaps"},
    1: {"dots": "●○○○", "label": "Weak", "description": "Few positive signals"},
}


# =============================================================================
# SIGNAL DEFINITIONS (6 Dimensions)
# =============================================================================

SIGNAL_DIMENSIONS = {
    "problem": {
        "name": "Problem Clarity",
        "strong_labels": ["Quantified Pain", "Urgent Problem", "Hair on Fire"],
        "moderate_labels": ["Clear Problem", "Validated Pain"],
        "weak_labels": ["Vague Problem", "Nice to Have"],
    },
    "solution": {
        "name": "Solution Feasibility",
        "strong_labels": ["Shipping", "Buildable", "MVP Ready"],
        "moderate_labels": ["Prototyped", "Technically Feasible"],
        "weak_labels": ["Concept Only", "Requires Breakthrough"],
    },
    "market": {
        "name": "Market Size",
        "strong_labels": ["Massive TAM", "Large SAM"],
        "moderate_labels": ["Growing Market", "Billion Dollar"],
        "weak_labels": ["Niche", "Limited"],
    },
    "moat": {
        "name": "Defensibility",
        "strong_labels": ["Network Effects", "Patents", "Proprietary Data"],
        "moderate_labels": ["Switching Costs", "Brand", "Expertise"],
        "weak_labels": ["First Mover Only", "None Identified"],
    },
    "velocity": {
        "name": "Traction",
        "strong_labels": ["Revenue", "Paying Customers", "Growth"],
        "moderate_labels": ["Pilots", "LOIs", "Waitlist"],
        "weak_labels": ["Pre-launch", "Idea Stage"],
    },
    "competition": {
        "name": "Competitive Landscape",
        "strong_labels": ["Gap Identified", "Clear Differentiation"],
        "moderate_labels": ["Validated Market", "Some Competitors"],
        "weak_labels": ["Saturated", "No Clear Wedge"],
    },
}


def get_archetype(archetype_id: str) -> Optional[Archetype]:
    """Get archetype by ID"""
    if archetype_id in ARCHETYPES:
        return ARCHETYPES[archetype_id]
    if archetype_id == "needs_more_data":
        return NEEDS_MORE_DATA
    return None


def get_conviction_display(level: int) -> Dict:
    """Get conviction display info (dots, label)"""
    return CONVICTION_LEVELS.get(level, CONVICTION_LEVELS[1])


def get_all_archetypes() -> List[Archetype]:
    """Get all archetypes in priority order"""
    # Sort by tier (1 = highest priority)
    return sorted(ARCHETYPES.values(), key=lambda a: a.tier.value)
