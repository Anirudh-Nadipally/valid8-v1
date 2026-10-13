from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import declarative_base, relationship
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

Base = declarative_base()

# --- SQLAlchemy Models (Database) ---

class AnalysisRecord(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    idea_title = Column(String)
    idea_problem = Column(Text)
    idea_solution = Column(Text)
    idea_audience = Column(String)
    idea_moat = Column(String)
    persona = Column(String)
    
    # Storing the full JSON analysis blob
    analysis_json = Column(JSON)
    
    # Relationships
    chat_history = relationship("ChatHistory", back_populates="analysis", cascade="all, delete-orphan")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    role = Column(String) # "user" or "assistant"
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("AnalysisRecord", back_populates="chat_history")

# --- Pydantic Models (API) ---

class IdeaInput(BaseModel):
    title: str
    problem: str
    solution: str
    targetAudience: str
    uniqueValue: str

class Competitor(BaseModel):
    name: str
    type: str
    reason: str

class LeanCanvas(BaseModel):
    problemSummary: str
    solutionSummary: str
    metrics: str
    channels: str
    revenue: str
    costs: str

class CustomerPersona(BaseModel):
    persona: str
    details: str

class MarketingHook(BaseModel):
    hook: str
    details: str

class Experiment(BaseModel):
    title: str
    action: str
    metric: str

class GoToMarket(BaseModel):
    firstCustomers: List[CustomerPersona]
    marketingHooks: List[MarketingHook]
    experiments: List[Experiment]

class Scores(BaseModel):
    problem: int
    solution: int
    market: int
    moat: int
    feasibility: int

class AnalysisResult(BaseModel):
    scores: Scores
    overallScore: int
    verdict: str
    strengths: List[str]
    weaknesses: List[str]
    competitors: List[Competitor]
    leanCanvas: LeanCanvas
    goToMarket: GoToMarket
    pivotSuggestion: str
    scoreTrace: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    id: int
    timestamp: datetime
    idea: IdeaInput
    analysis: AnalysisResult
    persona: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    analysisId: int
    message: str
    persona: str

class ScenarioRequest(BaseModel):
    analysisId: int
    scenario: str
    persona: str

class ScenarioResponse(BaseModel):
    verdict: str
    reasoning: str
    potentialScoreChange: str

class PitchRequest(BaseModel):
    analysisId: int

class PitchResponse(BaseModel):
    axiom: str
    northStar: Dict[str, str]
    narrative: Dict[str, str]
    hook: str

class LegalRequest(BaseModel):
    analysisId: int

class LegalRisk(BaseModel):
    title: str
    severity: str
    description: str

class LegalResponse(BaseModel):
    risks: List[LegalRisk]
    tip: str

class NameGenerationRequest(BaseModel):
    problem: str
    solution: str

class NameGenerationResponse(BaseModel):
    names: List[str]

class CompetitorAnalysisRequest(BaseModel):
    analysisId: int
    competitorName: str
    persona: str

class CompetitorAnalysisResponse(BaseModel):
    competitorName: str
    analysis: str

class MarketIntelRequest(BaseModel):
    analysisId: int

class MarketSegment(BaseModel):
    name: str
    size: str
    pain: str
    willingness: str
    description: str

class Channel(BaseModel):
    name: str
    type: str
    cost: str
    reach: str
    conversion: str

class PricingTier(BaseModel):
    tier: str
    price: str
    period: str
    features: List[str]

class MarketIntelResponse(BaseModel):
    segments: List[MarketSegment]
    channels: List[Channel]
    pricing: List[PricingTier]

class LeanCanvasRequest(BaseModel):
    analysisId: int

class LeanCanvasResponse(BaseModel):
    problemSummary: str
    solutionSummary: str
    metrics: str
    channels: str
    revenue: str
    costs: str
    uniqueValue: str
    unfairAdvantage: str
    customerSegments: str

class StrategyFlowRequest(BaseModel):
    analysisId: int
    section: str # "vision", "okrs", "roadmap"

class StrategyFlowResponse(BaseModel):
    vision: Optional[str] = None
    mission: Optional[str] = None
    objectives: Optional[List[Dict[str, Any]]] = None
    roadmap: Optional[List[Dict[str, Any]]] = None


# =============================================================================
# DETERMINISTIC SCORING PIPELINE MODELS
# =============================================================================

# --- SQLAlchemy Model for Pipeline Results ---

class PipelineRecord(Base):
    """Store deterministic pipeline results"""
    __tablename__ = "pipeline_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Scores
    final_score = Column(Float)
    grade = Column(String)
    
    # Full pipeline output as JSON
    extraction_json = Column(JSON)
    validation_json = Column(JSON)
    scoring_json = Column(JSON)
    presentation_json = Column(JSON, nullable=True)
    
    # Metadata
    rules_version = Column(String)
    pipeline_version = Column(String)
    persona = Column(String)


# --- Pydantic Models for Pipeline API ---

class DimensionScoreModel(BaseModel):
    score: int = Field(..., ge=0, le=100)
    weight: float
    weighted_score: float
    rules_triggered: List[str] = []


class RuleApplicationModel(BaseModel):
    rule_id: str
    dimension: str
    applied: bool
    points: int
    condition: Optional[str] = None
    reason: Optional[str] = None


class ScoringResultModel(BaseModel):
    final_score: float = Field(..., ge=0, le=100)
    grade: str
    dimension_scores: Dict[str, DimensionScoreModel]
    calculation_trace: List[RuleApplicationModel]
    rules_version: str
    scored_at: Optional[str] = None


class ValidationCheckModel(BaseModel):
    check_name: str
    check_type: Optional[str] = None
    status: str
    message: str
    field_affected: Optional[str] = None


class ValidationResultModel(BaseModel):
    status: str
    checks: List[ValidationCheckModel]
    is_valid_for_scoring: bool
    validator_version: str
    warnings_count: int = 0
    errors_count: int = 0


class PresentationResultModel(BaseModel):
    persona: str
    persona_display_name: str
    narrative: str
    generated_at: str
    locked_scores: Dict[str, Any]


class PipelineRequest(BaseModel):
    """Request body for pipeline analysis"""
    title: str
    problem: str
    solution: str
    targetAudience: Optional[str] = ""
    uniqueValue: Optional[str] = ""
    additionalContext: Optional[str] = ""
    persona: Optional[str] = "ruthless_vc"
    includePresentation: Optional[bool] = True


class PipelineResponse(BaseModel):
    """Full pipeline response"""
    status: str
    pipeline_results: Dict[str, Any]
    metadata: Dict[str, Any]
    # Legacy format for backwards compatibility
    legacy_analysis: Optional[Dict[str, Any]] = None


# =============================================================================
# V4: PATTERN-BASED CLASSIFICATION MODELS
# =============================================================================

# --- SQLAlchemy Model for V4 Pattern Results ---

class V4AnalysisRecord(Base):
    """Store V4 pattern-based analysis results"""
    __tablename__ = "v4_analyses"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Idea input
    idea_title = Column(String)
    idea_problem = Column(Text)
    idea_solution = Column(Text)
    idea_audience = Column(String)
    idea_moat = Column(String)
    
    # Pattern classification
    archetype_id = Column(String)
    archetype_name = Column(String)
    conviction = Column(Integer)  # 1-4
    
    # Full results as JSON
    signals_json = Column(JSON)
    classification_json = Column(JSON)
    grounding_json = Column(JSON, nullable=True)
    
    # Metadata
    pipeline_version = Column(String, default="4.0.0")


# --- Pydantic Models for V4 API ---

class V4PatternModel(BaseModel):
    """Pattern classification result"""
    id: str
    name: str
    icon: str
    tagline: str
    tier: int
    conviction: int
    conviction_dots: str
    conviction_label: str
    glow_color: str
    reasons: List[str]
    action_focus: str
    description: str


class V4SignalModel(BaseModel):
    """Individual signal dimension"""
    dimension: str
    name: str
    level: str  # "strong", "moderate", "weak"
    label: str
    value: Optional[str] = None
    source: Optional[str] = None
    progress: int = 50  # 0-100 for progress bar


class V4MarketDataModel(BaseModel):
    """Market intelligence with sources"""
    tam: Optional[str] = None
    tam_raw: Optional[int] = None
    sam: Optional[str] = None
    som: Optional[str] = None
    growth_rate: Optional[str] = None
    source: Optional[str] = None
    source_year: Optional[int] = None


class V4CompetitorModel(BaseModel):
    """Competitor with funding and gap analysis"""
    name: str
    funding_total: Optional[str] = None
    last_round: Optional[str] = None
    last_round_date: Optional[str] = None
    focus: Optional[str] = None
    gap: Optional[str] = None
    source: Optional[str] = None


class V4TrendModel(BaseModel):
    """Market trend indicator"""
    trend: str
    direction: str
    evidence: Optional[str] = None
    source: Optional[str] = None


class V4NextStepModel(BaseModel):
    """Actionable next step"""
    number: int
    action: str
    detail: str
    resources: List[Dict[str, str]] = []


class V4AnalysisRequest(BaseModel):
    """V4 analysis request"""
    title: str
    problem: str
    solution: str
    targetAudience: Optional[str] = ""
    uniqueValue: Optional[str] = ""
    industry: Optional[str] = ""  # For grounding queries
    geography: Optional[str] = "global"
    includeGrounding: Optional[bool] = True


class V4AnalysisResponse(BaseModel):
    """Complete V4 analysis response"""
    id: int
    timestamp: datetime
    
    # Idea echo
    idea: Dict[str, str]
    
    # Pattern classification
    pattern: V4PatternModel
    
    # Signal cards
    signals: List[V4SignalModel]
    
    # Market intelligence (grounded)
    market_intel: Optional[V4MarketDataModel] = None
    competitors: List[V4CompetitorModel] = []
    trends: List[V4TrendModel] = []
    
    # Actionable next steps
    next_steps: List[V4NextStepModel] = []
    
    # Metadata
    sources: List[str] = []
    grounding_timestamp: Optional[str] = None
    processing_time_ms: Optional[int] = None
