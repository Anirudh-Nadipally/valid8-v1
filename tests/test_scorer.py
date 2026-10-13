"""Layer 3 must be deterministic: same extraction in, same score out, no LLM."""
from scoring_pipeline.scorer import Scorer

SAMPLE = {}  # empty extraction exercises every rule's fallback path


def test_same_input_same_score():
    a = Scorer("balanced").score(SAMPLE)
    b = Scorer("balanced").score(SAMPLE)
    assert a["final_score"] == b["final_score"]
    assert a["dimension_scores"] == b["dimension_scores"]


def test_scores_are_bounded_and_explained():
    r = Scorer("balanced").score(SAMPLE)
    assert 0 <= r["final_score"] <= 100
    for dim in r["dimension_scores"].values():
        assert 0 <= dim["score"] <= 100
        assert isinstance(dim["rules_triggered"], list)


def test_weight_profile_changes_weighting_not_rules():
    bal = Scorer("balanced").score(SAMPLE)["dimension_scores"]
    vc = Scorer("vc_focused").score(SAMPLE)["dimension_scores"]
    assert {k: v["score"] for k, v in bal.items()} == {k: v["score"] for k, v in vc.items()}
