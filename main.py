import os
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from models import (
    Base, AnalysisRecord, ChatHistory, 
    AnalysisResponse, ChatRequest, ChatMessage, 
    ScenarioRequest, ScenarioResponse, 
    PitchRequest, PitchResponse, 
    LegalRequest, LegalResponse,
    NameGenerationRequest, NameGenerationResponse,
    CompetitorAnalysisRequest, CompetitorAnalysisResponse,
    MarketIntelRequest, MarketIntelResponse,
    LeanCanvasRequest, LeanCanvasResponse,
    StrategyFlowRequest, StrategyFlowResponse,
    # Pipeline models
    PipelineRecord, PipelineRequest, PipelineResponse
)
from services import GeminiClient, PDFProcessor, ReportGenerator, SearchService
from scoring_pipeline import ScoringPipeline

# --- Database Setup ---
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./valid8.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- App Setup ---
app = FastAPI(title="Valid8 Pro v3 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.middleware.trustedhost import TrustedHostMiddleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"] # Allow all hosts (tunneling)
)

ai_client = GeminiClient()

# Initialize the scoring pipeline
scoring_pipeline = ScoringPipeline(ai_client)

# --- Deterministic scoring helpers ---

# UI persona ids -> pipeline personas (each carries a weight profile)
UI_PERSONA_TO_PIPELINE = {
    "vc": "ruthless_vc",
    "bootstrapper": "indie_hacker",
    "researcher": "mom_test_coach",
    "roaster": "silicon_valley_satirist",
    "legal": "tech_advisor",
}


def build_score_trace(pipeline_result: dict) -> dict:
    """Compact, UI-ready trace: every dimension, its weight, and the rules that moved it."""
    scoring = pipeline_result["pipeline_results"]["scoring"]
    trace = scoring.get("calculation_trace", [])
    dims = []
    for key, d in scoring["dimension_scores"].items():
        fired = [
            {"id": t["rule_id"], "points": t.get("points", 0), "reason": t.get("reason", "")}
            for t in trace
            if t.get("dimension") == key and t.get("applied")
        ]
        dims.append({
            "key": key,
            "label": key.replace("_", " ").title(),
            "score": d["score"],
            "weight": d["weight"],
            "weighted": d["weighted_score"],
            "rules": fired,
        })
    return {
        "finalScore": scoring["final_score"],
        "grade": scoring["grade"],
        "rulesVersion": scoring.get("rules_version"),
        "weightProfile": pipeline_result["metadata"].get("weight_profile_used"),
        "validation": pipeline_result["pipeline_results"]["validation"]["status"],
        "dimensions": dims,
    }

# --- Endpoints ---

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_idea(
    title: Optional[str] = Form(None),
    problem: Optional[str] = Form(None),
    solution: Optional[str] = Form(None),
    targetAudience: Optional[str] = Form(None),
    uniqueValue: Optional[str] = Form(None),
    persona: str = Form("vc"),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # 1. Extract Content
    extracted_text = ""
    if file:
        try:
            content = await file.read()
            extracted_text = PDFProcessor.extract_text(content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid PDF: {str(e)}")
    
    # 2. Construct Prompt
    system_prompt = f"You are the '{persona}' persona. Analyze this startup idea."
    
    json_schema = """
    {
      "verdict": "string",
      "strengths": ["str"],
      "weaknesses": ["str"],
      "competitors": [{"name": "str", "type": "str", "reason": "str"}],
      "leanCanvas": { "problemSummary": "str", "solutionSummary": "str", "metrics": "str", "channels": "str", "revenue": "str", "costs": "str" },
      "goToMarket": { "firstCustomers": [{"persona": "str", "details": "str"}], "marketingHooks": [{"hook": "str", "details": "str"}], "experiments": [{"title": "str", "action": "str", "metric": "str"}] },
      "pivotSuggestion": "str"
    }
    """

    user_prompt = f"""
    Analyze the following startup idea and return a JSON object matching this schema: {json_schema}
    
    Idea Title: {title or "Unknown"}
    Problem: {problem or "Unknown"}
    Solution: {solution or "Unknown"}
    Audience: {targetAudience or "Unknown"}
    Moat: {uniqueValue or "Unknown"}
    
    Additional Context (from PDF):
    {extracted_text[:5000] if extracted_text else "None"}
    """

    # 3a. Deterministic score: the LLM only extracts fields, rules decide every point
    try:
        pipeline_result = scoring_pipeline.analyze(
            title=title or "Untitled Project",
            problem=problem or "",
            solution=solution or "",
            target_audience=targetAudience or "",
            unique_value=uniqueValue or "",
            additional_context=extracted_text[:5000] if extracted_text else "",
            source_type="pitch_deck" if file else "form_input",
            persona=UI_PERSONA_TO_PIPELINE.get(persona, "ruthless_vc"),
            include_presentation=False,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring pipeline failed: {str(e)}")

    # 3b. Qualitative analysis (verdict, competitors, canvas, go-to-market) from the LLM
    try:
        analysis_result = ai_client.generate_json(system_prompt, user_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Analysis Failed: {str(e)}")

    # 3c. Scores always come from the pipeline, never from the LLM's JSON
    legacy = scoring_pipeline.get_legacy_format(pipeline_result)
    analysis_result['scores'] = legacy['scores']
    analysis_result['overallScore'] = legacy['overallScore']
    analysis_result['scoreTrace'] = build_score_trace(pipeline_result)

    # 4. Save to DB
    # If PDF was used, fill in missing fields from analysis
    final_problem = problem or analysis_result['leanCanvas']['problemSummary']
    final_solution = solution or analysis_result['leanCanvas']['solutionSummary']
    final_audience = targetAudience or "See Analysis"
    final_moat = uniqueValue or "See Analysis"

    db_record = AnalysisRecord(
        idea_title=title or "Untitled Project",
        idea_problem=final_problem,
        idea_solution=final_solution,
        idea_audience=final_audience,
        idea_moat=final_moat,
        persona=persona,
        analysis_json=analysis_result
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return AnalysisResponse(
        id=db_record.id,
        timestamp=db_record.timestamp,
        idea={
            "title": db_record.idea_title,
            "problem": db_record.idea_problem,
            "solution": db_record.idea_solution,
            "targetAudience": db_record.idea_audience,
            "uniqueValue": db_record.idea_moat
        },
        analysis=analysis_result,
        persona=db_record.persona
    )

@app.get("/api/history", response_model=List[AnalysisResponse])
def get_history(db: Session = Depends(get_db)):
    records = db.query(AnalysisRecord).order_by(AnalysisRecord.timestamp.desc()).limit(20).all()
    return [
        AnalysisResponse(
            id=r.id,
            timestamp=r.timestamp,
            idea={
                "title": r.idea_title,
                "problem": r.idea_problem,
                "solution": r.idea_solution,
                "targetAudience": r.idea_audience,
                "uniqueValue": r.idea_moat
            },
            analysis=r.analysis_json,
            persona=r.persona
        ) for r in records
    ]

@app.post("/api/chat", response_model=ChatMessage)
def chat_with_persona(req: ChatRequest, db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == req.analysisId).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Save user message
    user_msg = ChatHistory(analysis_id=req.analysisId, role="user", content=req.message)
    db.add(user_msg)
    db.commit()

    # Get history
    history = db.query(ChatHistory).filter(ChatHistory.analysis_id == req.analysisId).order_by(ChatHistory.timestamp).all()
    history_text = "\n".join([f"{h.role}: {h.content}" for h in history])

    system_prompt = f"You are the '{req.persona}' persona. You have analyzed this idea: {record.idea_title}. Verdict: {record.analysis_json.get('verdict')}."
    user_prompt = f"Chat History:\n{history_text}\n\nRespond to the last user message."

    response_text = ai_client.generate_completion(system_prompt, user_prompt)

    # Save bot message
    bot_msg = ChatHistory(analysis_id=req.analysisId, role="assistant", content=response_text)
    db.add(bot_msg)
    db.commit()

    return ChatMessage(role="assistant", content=response_text)

@app.post("/api/scenario", response_model=ScenarioResponse)
def run_scenario(req: ScenarioRequest, db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == req.analysisId).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    system_prompt = f"You are the '{req.persona}' persona."
    user_prompt = f"""
    Original Idea: {record.idea_title}
    Original Verdict: {record.analysis_json.get('verdict')}
    
    User's Pivot Scenario: "{req.scenario}"
    
    Compare this pivot to the original.
    Return JSON: {{ "verdict": "Better" | "Worse" | "Sideways", "reasoning": "str", "potentialScoreChange": "+15" | "-10" | "+0" }}
    """
    
    return ai_client.generate_json(system_prompt, user_prompt)

@app.get("/api/report/{id}")
def download_report(id: int, db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    pdf_buffer = ReportGenerator.create_pdf_report(record.idea_title, record.analysis_json)
    
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{id}.pdf"}
    )

@app.post("/api/pitch-architect", response_model=PitchResponse)
def pitch_architect(req: PitchRequest, db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == req.analysisId).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Search for grounding
    search_query = f"market analysis for {record.idea_title} {record.idea_solution} competitors"
    search_results = SearchService.search(search_query)

    system_prompt = "You are a First Principles Strategist. Use the provided search context to ground your advice in reality."
    user_prompt = f"""
    Deconstruct this business: {record.idea_title}
    Problem: {record.idea_problem}
    Solution: {record.idea_solution}
    
    Real-world Market Context:
    {search_results}
    
    Return JSON:
    {{
      "axiom": "Fundamental truth about this specific market/problem",
      "northStar": {{ "metric": "Specific metric", "why": "Reasoning based on context" }},
      "narrative": {{ "oldWorld": "Current state", "insight": "Key insight", "newWorld": "Future state" }},
      "hook": "60-second pitch referencing real market dynamics"
    }}
    """
    return ai_client.generate_json(system_prompt, user_prompt)

@app.post("/api/market-intel", response_model=MarketIntelResponse)
def generate_market_intel(req: MarketIntelRequest, db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == req.analysisId).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    system_prompt = "You are a Go-To-Market Strategist."
    user_prompt = f"""
    Generate detailed market intelligence for:
    Title: {record.idea_title}
    Problem: {record.idea_problem}
    Solution: {record.idea_solution}
    
    Return JSON matching this schema:
    {{
      "segments": [{{ "name": "str", "size": "str", "pain": "High/Med/Low", "willingness": "High/Med/Low", "description": "str" }}],
      "channels": [{{ "name": "str", "type": "Inbound/Outbound/Paid", "cost": "High/Med/Low", "reach": "High/Med/Low", "conversion": "High/Med/Low" }}],
      "pricing": [{{ "tier": "str", "price": "str", "period": "month/year", "features": ["str"] }}]
    }}
    """
    
    result = ai_client.generate_json(system_prompt, user_prompt)
    
    # Update DB
    current_analysis = dict(record.analysis_json)
    current_analysis['marketIntel'] = result
    record.analysis_json = current_analysis
    db.commit()
    
    return result

@app.post("/api/lean-canvas", response_model=LeanCanvasResponse)
def generate_lean_canvas(req: LeanCanvasRequest, db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == req.analysisId).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    system_prompt = "You are a Lean Startup Expert. Be specific, detailed, and consistent."
    user_prompt = f"""
    Generate a complete Lean Canvas for:
    Title: {record.idea_title}
    Problem: {record.idea_problem}
    Solution: {record.idea_solution}
    
    CRITICAL INSTRUCTIONS:
    1. Do NOT use phrases like "See Analysis" or "Refer to...".
    2. Fill in EVERY field with specific, actionable details based on the idea.
    3. Be consistent.
    
    Return JSON matching this schema:
    {{
      "problemSummary": "Top 3 problems",
      "solutionSummary": "Top 3 features",
      "metrics": "Key metrics (e.g. CAC, LTV)",
      "channels": "Path to customers",
      "revenue": "Revenue model",
      "costs": "Cost structure",
      "uniqueValue": "Single, clear, compelling message",
      "unfairAdvantage": "Can't be easily copied or bought",
      "customerSegments": "Target customers"
    }}
    """
    
    # Use low temperature for consistency
    result = ai_client.generate_json(system_prompt, user_prompt)
    
    # Update DB
    current_analysis = dict(record.analysis_json)
    current_analysis['leanCanvas'] = result
    record.analysis_json = current_analysis
    db.commit()
    
    return result

@app.post("/api/strategy-flow", response_model=StrategyFlowResponse)
def generate_strategy_flow(req: StrategyFlowRequest, db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == req.analysisId).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    system_prompt = "You are a Strategic Planner. Be precise and consistent."
    
    if req.section == "vision":
        user_prompt = f"""
        Generate Vision and Mission for:
        Title: {record.idea_title}
        Problem: {record.idea_problem}
        Solution: {record.idea_solution}
        
        Return JSON: {{ "vision": "Future state (10 years)", "mission": "What we do every day" }}
        """
    elif req.section == "okrs":
        user_prompt = f"""
        Generate 3 Strategic Objectives (OKRs) for:
        Title: {record.idea_title}
        
        Return JSON: {{ "objectives": [{{ "objective": "str", "keyResults": ["str", "str"] }}] }}
        """
    elif req.section == "roadmap":
        user_prompt = f"""
        Generate a 4-phase Roadmap for:
        Title: {record.idea_title}
        
        Return JSON: {{ "roadmap": [{{ "phase": "Phase 1: Name", "duration": "3 months", "milestones": ["str", "str"] }}] }}
        """
    else:
        raise HTTPException(status_code=400, detail="Invalid section")

    # Use low temperature for consistency
    result = ai_client.generate_json(system_prompt, user_prompt)
    
    # Update DB (partial update logic would be complex here, so we just return for now or update if structure exists)
    # For simplicity, we'll just return the result and let frontend handle state, 
    # or we could update a 'strategyFlow' field in analysis_json if we want persistence.
    # Let's persist it.
    current_analysis = dict(record.analysis_json)
    if 'strategyFlow' not in current_analysis:
        current_analysis['strategyFlow'] = {}
    
    if req.section == "vision":
        current_analysis['strategyFlow']['vision'] = result.get('vision')
        current_analysis['strategyFlow']['mission'] = result.get('mission')
    elif req.section == "okrs":
        current_analysis['strategyFlow']['objectives'] = result.get('objectives')
    elif req.section == "roadmap":
        current_analysis['strategyFlow']['roadmap'] = result.get('roadmap')
        
    record.analysis_json = current_analysis
    db.commit()

    return result

@app.post("/api/legal-check", response_model=LegalResponse)
def legal_check(req: LegalRequest, db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == req.analysisId).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    system_prompt = "You are a Startup Lawyer."
    user_prompt = f"""
    Identify legal risks for: {record.idea_title}
    Description: {record.idea_solution}
    
    Return JSON:
    {{
      "risks": [{{ "title": "str", "severity": "High/Medium/Low", "description": "str" }}],
      "tip": "One safe harbor tip"
    }}
    """
    return ai_client.generate_json(system_prompt, user_prompt)

@app.post("/api/generate-names", response_model=NameGenerationResponse)
def generate_names(req: NameGenerationRequest):
    system_prompt = "You are a Branding Expert."
    user_prompt = f"""
    Generate 5 venture names for:
    Problem: {req.problem}
    Solution: {req.solution}
    
    Return JSON: {{ "names": ["str", "str", "str", "str", "str"] }}
    """
    return ai_client.generate_json(system_prompt, user_prompt)

@app.post("/api/competitor-weakness", response_model=CompetitorAnalysisResponse)
def analyze_competitor(req: CompetitorAnalysisRequest, db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == req.analysisId).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    system_prompt = f"You are the '{req.persona}' persona."
    user_prompt = f"""
    Startup: {record.idea_title}
    Competitor: {req.competitorName}
    
    Find one exploitable weakness of this competitor.
    """
    analysis = ai_client.generate_completion(system_prompt, user_prompt)
    return CompetitorAnalysisResponse(competitorName=req.competitorName, analysis=analysis)


# =============================================================================
# DETERMINISTIC SCORING PIPELINE ENDPOINTS
# =============================================================================

@app.post("/api/pipeline/analyze", response_model=PipelineResponse)
async def pipeline_analyze(
    req: PipelineRequest,
    db: Session = Depends(get_db)
):
    """
    Run the full deterministic scoring pipeline
    
    This endpoint provides:
    - Layer 1: LLM Extraction (bounded, with schema)
    - Layer 2: Deterministic Validation (pure code, no LLM)
    - Layer 3: Rule-Based Scoring (no ML, no randomness)
    - Layer 4: LLM Presentation (optional, scores locked)
    
    Same input ALWAYS produces same scores (deterministic).
    """
    try:
        # Run the pipeline
        result = scoring_pipeline.analyze(
            title=req.title,
            problem=req.problem,
            solution=req.solution,
            target_audience=req.targetAudience or "",
            unique_value=req.uniqueValue or "",
            additional_context=req.additionalContext or "",
            source_type="form_input",
            persona=req.persona or "ruthless_vc",
            include_presentation=req.includePresentation if req.includePresentation is not None else True
        )
        
        # Get legacy format for backwards compatibility
        legacy_analysis = scoring_pipeline.get_legacy_format(result)
        
        # Save to database
        pipeline_record = PipelineRecord(
            final_score=result['pipeline_results']['scoring']['final_score'],
            grade=result['pipeline_results']['scoring']['grade'],
            extraction_json=result['pipeline_results']['extraction']['data'],
            validation_json=result['pipeline_results']['validation'],
            scoring_json=result['pipeline_results']['scoring'],
            presentation_json=result['pipeline_results'].get('presentation'),
            rules_version=result['pipeline_results']['scoring']['rules_version'],
            pipeline_version=result['metadata']['pipeline_version'],
            persona=req.persona or "ruthless_vc"
        )
        db.add(pipeline_record)
        db.commit()
        
        return PipelineResponse(
            status=result['status'],
            pipeline_results=result['pipeline_results'],
            metadata=result['metadata'],
            legacy_analysis=legacy_analysis
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline analysis failed: {str(e)}")


@app.get("/api/pipeline/rules")
def get_pipeline_rules():
    """Get current scoring rules version and configuration"""
    import yaml
    from pathlib import Path
    
    rules_path = Path(__file__).parent / 'scoring_pipeline' / 'rules' / 'scoring-rules.yaml'
    weights_path = Path(__file__).parent / 'scoring_pipeline' / 'rules' / 'weights.yaml'
    
    try:
        with open(rules_path, 'r') as f:
            rules = yaml.safe_load(f)
        with open(weights_path, 'r') as f:
            weights = yaml.safe_load(f)
        
        return {
            'rules_version': rules.get('version', '1.0.0'),
            'weights_version': weights.get('version', '1.0.0'),
            'dimensions': list(weights.get('weights', {}).keys()),
            'weight_profiles': list(weights.get('profiles', {}).keys()),
            'grade_thresholds': rules.get('grade_thresholds', {}),
            'industry_multipliers': rules.get('industry_multipliers', {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load rules: {str(e)}")


@app.get("/api/pipeline/personas")
def get_available_personas():
    """Get available personas for scoring presentation"""
    return scoring_pipeline.presenter.get_available_personas()


@app.post("/api/analyze-deterministic", response_model=AnalysisResponse)
async def analyze_idea_deterministic(
    title: Optional[str] = Form(None),
    problem: Optional[str] = Form(None),
    solution: Optional[str] = Form(None),
    targetAudience: Optional[str] = Form(None),
    uniqueValue: Optional[str] = Form(None),
    persona: str = Form("vc"),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Enhanced analyze endpoint that uses deterministic scoring pipeline
    Returns the same response format as /api/analyze for backwards compatibility
    """
    # 1. Extract Content from PDF if provided
    extracted_text = ""
    if file:
        try:
            content = await file.read()
            extracted_text = PDFProcessor.extract_text(content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid PDF: {str(e)}")
    
    # 2. Map persona name
    persona_map = {
        'vc': 'ruthless_vc',
        'indie': 'indie_hacker',
        'mom_test': 'mom_test_coach',
        'tech': 'tech_advisor',
        'satirist': 'silicon_valley_satirist'
    }
    pipeline_persona = persona_map.get(persona, 'ruthless_vc')
    
    # 3. Run the deterministic pipeline
    try:
        result = scoring_pipeline.analyze(
            title=title or "Untitled Project",
            problem=problem or "",
            solution=solution or "",
            target_audience=targetAudience or "",
            unique_value=uniqueValue or "",
            additional_context=extracted_text,
            source_type="pitch_deck" if file else "form_input",
            persona=pipeline_persona,
            include_presentation=True
        )
        
        # Convert to legacy format
        legacy_analysis = scoring_pipeline.get_legacy_format(result)
        
        # Save to DB
        db_record = AnalysisRecord(
            idea_title=title or "Untitled Project",
            idea_problem=problem or legacy_analysis['leanCanvas']['problemSummary'],
            idea_solution=solution or legacy_analysis['leanCanvas']['solutionSummary'],
            idea_audience=targetAudience or "See Analysis",
            idea_moat=uniqueValue or "See Analysis",
            persona=persona,
            analysis_json=legacy_analysis
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        return AnalysisResponse(
            id=db_record.id,
            timestamp=db_record.timestamp,
            idea={
                "title": db_record.idea_title,
                "problem": db_record.idea_problem,
                "solution": db_record.idea_solution,
                "targetAudience": db_record.idea_audience,
                "uniqueValue": db_record.idea_moat
            },
            analysis=legacy_analysis,
            persona=db_record.persona
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deterministic Analysis Failed: {str(e)}")


# =============================================================================
# V4: PATTERN-BASED CLASSIFICATION ENDPOINTS
# =============================================================================

from models import (
    V4AnalysisRecord, V4AnalysisRequest, V4AnalysisResponse,
    V4PatternModel, V4SignalModel, V4MarketDataModel,
    V4CompetitorModel, V4TrendModel, V4NextStepModel
)
from scoring_pipeline import (
    classify_archetype, extract_signals_from_extracted_data,
    GroundingService, grounding_result_to_dict,
    ARCHETYPES, get_archetype
)
import time
import asyncio


@app.post("/api/v4/analyze", response_model=V4AnalysisResponse)
async def v4_analyze_idea(
    req: V4AnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    V4 Pattern-based analysis endpoint
    
    Returns:
    - Pattern classification (archetype + conviction)
    - Signal cards (6 dimensions)
    - Market intelligence (grounded with Gemini)
    - Competitor data
    - Actionable next steps
    """
    start_time = time.time()
    
    try:
        # Step 1: Extract structured data using existing pipeline
        extraction_prompt = f"""
        Analyze this startup idea and extract structured data.
        
        Title: {req.title}
        Problem: {req.problem}
        Solution: {req.solution}
        Target Audience: {req.targetAudience}
        Unique Value: {req.uniqueValue}
        
        Return JSON with these fields:
        {{
            "problem": {{
                "severity": "critical|high|medium|low",
                "quantified": true|false,
                "frequency": "daily|weekly|monthly|occasional"
            }},
            "solution": {{
                "stage": "launched|mvp|prototype|concept",
                "technical_feasibility": "proven|achievable|unproven"
            }},
            "target_audience": {{
                "specificity": "specific|reachable|generic|unclear"
            }},
            "market": {{
                "tam": 0
            }},
            "team": {{
                "size": 1,
                "relevant_experience": false
            }},
            "competitors": [],
            "moat": "{req.uniqueValue}",
            "revenue": {{
                "has_revenue": false
            }},
            "geography": "{req.geography}",
            "business_model": ""
        }}
        """
        
        extracted_data = ai_client.generate_json(
            "You are a startup analyst. Extract structured data from the pitch.",
            extraction_prompt
        )
        
        # Step 2: Convert to signals
        signals = extract_signals_from_extracted_data(extracted_data)
        
        # Step 3: Classify pattern (DETERMINISTIC - NO LLM)
        classification = classify_archetype(signals)
        
        # Step 4: Run grounding (optional, parallel)
        grounding_data = None
        if req.includeGrounding:
            try:
                # Determine industry from problem/solution
                industry = req.industry or f"{req.problem[:50]} {req.solution[:50]}"
                grounding_service = GroundingService()
                grounding_result = await grounding_service.enrich_idea(
                    industry=industry,
                    geography=req.geography,
                    problem=req.problem,
                    solution=req.solution
                )
                grounding_data = grounding_result_to_dict(grounding_result)
            except Exception as e:
                print(f"Grounding failed (non-fatal): {e}")
        
        # Step 5: Generate signals for UI
        signal_cards = _generate_signal_cards(signals, extracted_data, grounding_data)
        
        # Step 6: Generate next steps based on pattern
        next_steps = _generate_next_steps(classification.archetype_id, signals)
        
        # Step 7: Save to database
        db_record = V4AnalysisRecord(
            idea_title=req.title,
            idea_problem=req.problem,
            idea_solution=req.solution,
            idea_audience=req.targetAudience,
            idea_moat=req.uniqueValue,
            archetype_id=classification.archetype_id,
            archetype_name=classification.archetype_name,
            conviction=classification.conviction,
            signals_json=signals,
            classification_json={
                "archetype_id": classification.archetype_id,
                "conviction": classification.conviction,
                "reasons": classification.reasons
            },
            grounding_json=grounding_data
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Build response
        return V4AnalysisResponse(
            id=db_record.id,
            timestamp=db_record.timestamp,
            idea={
                "title": req.title,
                "problem": req.problem,
                "solution": req.solution,
                "targetAudience": req.targetAudience or "",
                "uniqueValue": req.uniqueValue or ""
            },
            pattern=V4PatternModel(
                id=classification.archetype_id,
                name=classification.archetype_name,
                icon=classification.icon,
                tagline=classification.tagline,
                tier=classification.tier,
                conviction=classification.conviction,
                conviction_dots=classification.conviction_dots,
                conviction_label=classification.conviction_label,
                glow_color=classification.glow_color,
                reasons=classification.reasons,
                action_focus=classification.action_focus,
                description=classification.description
            ),
            signals=signal_cards,
            market_intel=V4MarketDataModel(**grounding_data["market"]) if grounding_data else None,
            competitors=[
                V4CompetitorModel(**c) for c in (grounding_data.get("competitors", []) if grounding_data else [])
            ],
            trends=[
                V4TrendModel(**t) for t in (grounding_data.get("trends", []) if grounding_data else [])
            ],
            next_steps=next_steps,
            sources=grounding_data.get("sources", []) if grounding_data else [],
            grounding_timestamp=grounding_data.get("last_updated") if grounding_data else None,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"V4 Analysis Failed: {str(e)}")


@app.post("/api/v4/classify")
async def v4_quick_classify(req: V4AnalysisRequest):
    """
    Quick pattern classification without grounding
    Returns pattern + conviction only (faster)
    """
    try:
        # Simple signal extraction from input
        signals = {
            "problem": "quantified_pain" if any(c.isdigit() for c in req.problem) else "clear_pain",
            "solution": "buildable" if len(req.solution) > 50 else "concept",
            "customer": "specific" if len(req.targetAudience or "") > 20 else "generic",
            "differentiation": "clear" if len(req.uniqueValue or "") > 30 else "weak",
            "market": "medium",
            "competition": "emerging"
        }
        
        classification = classify_archetype(signals)
        
        return {
            "pattern": {
                "id": classification.archetype_id,
                "name": classification.archetype_name,
                "icon": classification.icon,
                "conviction": classification.conviction,
                "conviction_dots": classification.conviction_dots
            },
            "tagline": classification.tagline,
            "action_focus": classification.action_focus
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@app.get("/api/v4/archetypes")
def v4_get_archetypes():
    """Get all available archetypes with their definitions"""
    return {
        "archetypes": [
            {
                "id": a.id,
                "name": a.name,
                "icon": a.icon,
                "tagline": a.tagline,
                "tier": a.tier.value,
                "glow_color": a.glow_color,
                "description": a.description,
                "action_focus": a.action_focus
            }
            for a in ARCHETYPES.values()
        ]
    }


@app.get("/api/v4/history")
def v4_get_history(db: Session = Depends(get_db)):
    """Get V4 analysis history with patterns"""
    records = db.query(V4AnalysisRecord).order_by(V4AnalysisRecord.timestamp.desc()).limit(20).all()
    
    return [
        {
            "id": r.id,
            "timestamp": r.timestamp.isoformat(),
            "title": r.idea_title,
            "archetype_id": r.archetype_id,
            "archetype_name": r.archetype_name,
            "conviction": r.conviction,
            "icon": get_archetype(r.archetype_id).icon if get_archetype(r.archetype_id) else "❓"
        }
        for r in records
    ]


def _generate_signal_cards(signals: dict, extracted_data: dict, grounding_data: dict) -> list:
    """Generate signal cards for the 6 dimensions"""
    cards = []
    
    # Problem dimension
    problem_signal = signals.get("problem", "unclear")
    cards.append(V4SignalModel(
        dimension="problem",
        name="Problem Clarity",
        level="strong" if "quantified" in problem_signal or "urgent" in problem_signal else ("moderate" if "clear" in problem_signal else "weak"),
        label="Quantified Pain" if "quantified" in problem_signal else ("Clear Problem" if "clear" in problem_signal else "Needs Definition"),
        value=extracted_data.get("problem", {}).get("severity", "") if isinstance(extracted_data.get("problem"), dict) else "",
        progress=85 if "quantified" in problem_signal else (60 if "clear" in problem_signal else 30)
    ))
    
    # Solution dimension
    solution_signal = signals.get("solution", "unclear")
    cards.append(V4SignalModel(
        dimension="solution",
        name="Solution Feasibility",
        level="strong" if solution_signal in ["shipping", "buildable"] else ("moderate" if solution_signal == "prototyped" else "weak"),
        label="Buildable" if solution_signal in ["shipping", "buildable"] else "Concept Stage",
        progress=80 if solution_signal == "shipping" else (65 if solution_signal == "buildable" else 35)
    ))
    
    # Market dimension - use grounding if available
    market_signal = signals.get("market", "unclear")
    market_value = None
    market_source = None
    if grounding_data and grounding_data.get("market", {}).get("tam"):
        market_value = grounding_data["market"]["tam"]
        market_source = grounding_data["market"].get("source")
    
    cards.append(V4SignalModel(
        dimension="market",
        name="Market Size",
        level="strong" if market_signal == "massive" else ("moderate" if market_signal in ["large", "medium"] else "weak"),
        label=f"{market_value}" if market_value else ("Massive TAM" if market_signal == "massive" else "Limited Market"),
        value=grounding_data["market"].get("growth_rate") if grounding_data else None,
        source=market_source,
        progress=95 if market_signal == "massive" else (70 if market_signal == "large" else 40)
    ))
    
    # Moat dimension
    diff_signal = signals.get("differentiation", "unclear")
    cards.append(V4SignalModel(
        dimension="moat",
        name="Defensibility",
        level="strong" if diff_signal == "clear" else ("moderate" if diff_signal == "moderate" else "weak"),
        label="Clear Moat" if diff_signal == "clear" else "Needs Work",
        progress=75 if diff_signal == "clear" else (50 if diff_signal == "moderate" else 25)
    ))
    
    # Velocity dimension
    revenue_signal = signals.get("revenue", "none")
    cards.append(V4SignalModel(
        dimension="velocity",
        name="Traction",
        level="strong" if revenue_signal == "has_revenue" else ("moderate" if revenue_signal == "pilots" else "weak"),
        label="Has Revenue" if revenue_signal == "has_revenue" else "Pre-Launch",
        progress=90 if revenue_signal == "has_revenue" else (45 if revenue_signal == "pilots" else 20)
    ))
    
    # Competition dimension
    comp_signal = signals.get("competition", "none")
    cards.append(V4SignalModel(
        dimension="competition",
        name="Competition",
        level="moderate" if comp_signal == "validated" else ("weak" if comp_signal == "saturated" else "moderate"),
        label="Gap Identified" if comp_signal == "validated" else ("Crowded" if comp_signal == "saturated" else "Emerging"),
        progress=70 if comp_signal == "validated" else (30 if comp_signal == "saturated" else 50)
    ))
    
    return cards


def _generate_next_steps(archetype_id: str, signals: dict) -> list:
    """Generate 3 actionable next steps based on pattern and signals"""
    
    # Default steps by archetype
    archetype_steps = {
        "painkiller": [
            {"action": "Validate Willingness to Pay", "detail": "Talk to 5 customers this week. Get price feedback."},
            {"action": "Build MVP", "detail": "Ship the core feature in 2 weeks."},
            {"action": "Get First Revenue", "detail": "Close 1 paying customer before anything else."}
        ],
        "rocket": [
            {"action": "Prove Unit Economics", "detail": "Calculate and validate your CAC:LTV ratio."},
            {"action": "Build Case Study", "detail": "Document 1 customer success story with metrics."},
            {"action": "Prepare Pitch Deck", "detail": "Create a 10-slide deck for investor conversations."}
        ],
        "execution_play": [
            {"action": "Study Competitor Weakness", "detail": "Deep dive into top competitor's gaps."},
            {"action": "Define Your Wedge", "detail": "What can you do 10x better?"},
            {"action": "Move Fast", "detail": "Ship faster than incumbents. Speed is your moat."}
        ],
        "vitamin": [
            {"action": "Find the Urgency", "detail": "What triggers make this a must-have?"},
            {"action": "Reposition Around Pain", "detail": "Find a hair-on-fire moment."},
            {"action": "Talk to 20 Users", "detail": "Discover when they actually need this."}
        ],
        "moonshot": [
            {"action": "De-risk the Core Thesis", "detail": "Prove the hardest technical challenge first."},
            {"action": "Find Early Believers", "detail": "Get 3 design partners to test with."},
            {"action": "Set Clear Milestones", "detail": "Define what success looks like in 6 months."}
        ],
        "lifestyle": [
            {"action": "Optimize for Profit", "detail": "Focus on margins, not growth at all costs."},
            {"action": "Bootstrap Smart", "detail": "Don't raise VC money for this."},
            {"action": "Build Your Audience", "detail": "Content marketing > paid acquisition."}
        ],
        "solution_seeking_problem": [
            {"action": "Stop Building", "detail": "Pause development immediately."},
            {"action": "Talk to 50 Users", "detail": "Find who has the problem you're solving."},
            {"action": "Pivot if Needed", "detail": "Be willing to change the solution."}
        ],
        "red_ocean": [
            {"action": "Find a 10x Wedge", "detail": "What makes you dramatically better?"},
            {"action": "Consider Pivoting", "detail": "Is there an adjacent uncontested market?"},
            {"action": "Niche Down", "detail": "Own a small segment before expanding."}
        ]
    }
    
    steps = archetype_steps.get(archetype_id, archetype_steps["vitamin"])
    
    return [
        V4NextStepModel(
            number=i+1,
            action=step["action"],
            detail=step["detail"],
            resources=[]
        )
        for i, step in enumerate(steps[:3])
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

