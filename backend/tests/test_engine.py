"""Test the core engine"""
import pytest
import engine


def test_score_answers_empty():
    """Empty answers should return neutral profile"""
    profile = engine.score_answers({})
    assert profile is not None
    assert "interests" in profile
    assert "personality" in profile


def test_score_answers_basic():
    """Basic answers should produce valid profile"""
    answers = {
        "stage": "university",
        "goals": "become a software engineer",
        "i_i1": 5, "i_i2": 5, "i_i3": 4,
        "i_r1": 3, "i_r2": 3,
        "p_o1": 4, "p_o2": 2,
        "s_programming": 4, "s_quant": 4,
    }
    profile = engine.score_answers(answers)
    assert 0 <= profile["interests"]["I"] <= 100
    assert 0 <= profile["skills"]["programming"] <= 5


def test_holland_code():
    """Holland code should be 3 letters"""
    answers = {"i_i1": 5, "i_i2": 5, "i_i3": 4}
    profile = engine.score_answers(answers)
    code = engine.holland_code(profile)
    assert len(code) == 3
    assert all(c in "RIASEC" for c in code)


def test_recommend_returns_list():
    """Recommendations should return list of dicts"""
    answers = {"i_i1": 5, "i_i2": 4}
    profile = engine.score_answers(answers)
    recs = engine.recommend(profile, limit=10)
    assert isinstance(recs, list)
    assert len(recs) <= 10
    assert all("career" in r for r in recs)
    assert all("score" in r for r in recs)


def test_analyze_10_levels():
    """10-level analysis should return 10 levels"""
    answers = {"i_i1": 4, "p_o1": 4}
    profile = engine.score_answers(answers)
    analysis = engine.analyze_10_levels(profile)
    assert len(analysis) == 10
    assert all(f"level_{i}" in analysis for i in range(1, 11))


def test_recommendation_scores_are_valid():
    """Every recommendation should have a valid score and percentage."""
    profile = engine.empty_scores()
    recommendations = engine.recommend(profile, limit=10)

    assert recommendations
    for item in recommendations:
        assert 0.0 <= item["score"] <= 1.0
        assert 0 <= item["match_percentage"] <= 100
        assert item["match_percentage"] == round(item["score"] * 100)


def test_interested_feedback_increases_score():
    """Marking a career interested should increase its score."""
    profile = engine.empty_scores()
    baseline = engine.recommend(profile, limit=len(engine.CAREERS))
    career_id = baseline[0]["career"]["id"]

    updated = engine.recommend(
        profile,
        feedback={career_id: "interested"},
        limit=len(engine.CAREERS),
    )

    baseline_score = next(
        item["score"] for item in baseline
        if item["career"]["id"] == career_id
    )
    updated_score = next(
        item["score"] for item in updated
        if item["career"]["id"] == career_id
    )

    assert updated_score > baseline_score


def test_not_for_me_feedback_decreases_score():
    """Rejecting a career should decrease its score."""
    profile = engine.empty_scores()
    baseline = engine.recommend(profile, limit=len(engine.CAREERS))
    career_id = baseline[0]["career"]["id"]

    updated = engine.recommend(
        profile,
        feedback={career_id: "not_for_me"},
        limit=len(engine.CAREERS),
    )

    baseline_score = next(
        item["score"] for item in baseline
        if item["career"]["id"] == career_id
    )
    updated_score = next(
        item["score"] for item in updated
        if item["career"]["id"] == career_id
    )

    assert updated_score < baseline_score


def test_recommendations_respect_limit():
    """The engine should respect the requested result count."""
    profile = engine.empty_scores()

    assert len(engine.recommend(profile, limit=3)) <= 3
    assert len(engine.recommend(profile, limit=5)) <= 5
