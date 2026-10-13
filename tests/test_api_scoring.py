"""The UI's /api/analyze must take its scores from the rules engine, even when the LLM tries to set them."""
import json
from fastapi.testclient import TestClient

import main
from scoring_pipeline.scorer import Scorer

EXTRACTION = {
    "idea_core": {
        "problem_statement": "Founders lose good startup ideas in notes apps and never test them against real demand.",
        "solution_description": "A validation dashboard that scores each idea, maps competitors and drafts a go-to-market plan.",
        "target_customer": "Solo founders and student builders",
        "value_proposition": "Opinionated scoring plus a pivot lab",
        "competitors_mentioned": ["Notion", "ChatGPT"],
        "differentiation": "Rule-based scores with a reason for every point",
    },
    "market_classification": {"industry_vertical": "ai_ml", "business_model": "freemium",
                              "target_geography": "global", "customer_segment": "prosumer"},
    "stage_indicators": {"development_stage": "prototype", "team_size": "solo",
                         "funding_stage": "bootstrapped", "has_revenue": False, "has_users": True},
    "extraction_metadata": {"source_type": "form_input", "extraction_confidence": "high",
                            "fields_extracted": ["problem_statement"], "fields_inferred": [], "extraction_notes": None},
}

LLM_QUALITATIVE = {
    # The model tries to hand out perfect scores. They must be ignored.
    "scores": {"problem": 99, "solution": 99, "market": 99, "moat": 99, "feasibility": 99},
    "overallScore": 99,
    "verdict": "Promising but thin.",
    "strengths": ["a"], "weaknesses": ["b"],
    "competitors": [{"name": "Notion", "type": "Indirect", "reason": "notes"}],
    "leanCanvas": {"problemSummary": "p", "solutionSummary": "s", "metrics": "m",
                   "channels": "c", "revenue": "r", "costs": "c"},
    "goToMarket": {"firstCustomers": [], "marketingHooks": [], "experiments": []},
    "pivotSuggestion": "x",
}


def fake_llm(monkeypatch):
    monkeypatch.setattr(main.ai_client, "generate_completion",
                        lambda system, user, temperature=0.7: json.dumps(EXTRACTION))
    monkeypatch.setattr(main.ai_client, "generate_json", lambda system, user: json.loads(json.dumps(LLM_QUALITATIVE)))


def post(client, persona="vc"):
    return client.post("/api/analyze", data={
        "title": "IdeaVault", "problem": EXTRACTION["idea_core"]["problem_statement"],
        "solution": EXTRACTION["idea_core"]["solution_description"], "persona": persona,
    })


def test_llm_cannot_set_scores(monkeypatch):
    fake_llm(monkeypatch)
    r = post(TestClient(main.app))
    assert r.status_code == 200, r.text
    a = r.json()["analysis"]
    assert a["overallScore"] != 99
    assert 99 not in a["scores"].values()


def test_score_matches_rules_engine_and_is_traced(monkeypatch):
    fake_llm(monkeypatch)
    a = post(TestClient(main.app), persona="vc").json()["analysis"]
    expected = Scorer("vc_focused").score(EXTRACTION)
    trace = a["scoreTrace"]
    assert trace["finalScore"] == expected["final_score"]
    assert a["overallScore"] == int(expected["final_score"])
    for dim in trace["dimensions"]:
        assert dim["score"] == expected["dimension_scores"][dim["key"]]["score"]
        assert all(rule["id"] for rule in dim["rules"])


def test_same_input_same_score(monkeypatch):
    fake_llm(monkeypatch)
    c = TestClient(main.app)
    assert post(c).json()["analysis"]["scoreTrace"] == post(c).json()["analysis"]["scoreTrace"]
