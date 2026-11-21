"""Tests for the matching engine."""

from src.matching import ResumeScorer

UNRELATED_RESUME = """
RAVI KUMAR
SUMMARY
Head chef with 8 years of experience in hotel kitchens.
EXPERIENCE
Head Chef - Grand Hotel (2016 - 2024)
- Menu planning, inventory and food safety
EDUCATION
Diploma in Hotel Management
"""


def test_relevant_resume_ranks_first(sample_resume, sample_jd):
    _, results = ResumeScorer().score_texts(
        sample_jd, [("chef.txt", UNRELATED_RESUME), ("john.txt", sample_resume)]
    )
    assert [r.filename for r in results] == ["john.txt", "chef.txt"]
    assert results[0].overall_score > results[1].overall_score + 0.3


def test_scores_are_between_zero_and_one(sample_resume, sample_jd):
    _, results = ResumeScorer().score_texts(sample_jd, [("john.txt", sample_resume)])
    r = results[0]
    for value in (r.overall_score, r.tfidf_score, r.entity_score, *r.component_scores.values()):
        assert 0.0 <= value <= 1.0


def test_matched_and_missing_skills(sample_resume, sample_jd_simple):
    _, results = ResumeScorer().score_texts(sample_jd_simple, [("john.txt", sample_resume)])
    r = results[0]
    assert "Python" in r.matched_skills
    assert "SQL" in r.matched_skills
    assert r.missing_skills == []


def test_missing_required_skill_is_reported():
    _, results = ResumeScorer().score_texts(
        "Data engineer. Requirements: Python and Kafka.", [("a.txt", "Python developer")]
    )
    assert results[0].missing_skills == ["Kafka"]
    assert results[0].component_scores["skills"] == 0.5


def test_experience_component_caps_at_one():
    job = "Requirements: Python. 2+ years of experience."
    _, results = ResumeScorer().score_texts(
        job,
        [
            ("senior.txt", "SUMMARY\nPython developer with 6 years of experience."),
            ("junior.txt", "SUMMARY\nPython developer with 1 year of experience."),
        ],
    )
    by_name = {r.filename: r for r in results}
    assert by_name["senior.txt"].component_scores["experience"] == 1.0
    assert by_name["junior.txt"].component_scores["experience"] == 0.5


def test_job_without_structured_requirements_uses_tfidf_only():
    _, results = ResumeScorer().score_texts(
        "We are hiring someone to cook pasta and bake bread in our kitchen.",
        [("chef.txt", "I cook pasta and bake bread every day.")],
    )
    r = results[0]
    assert r.component_scores == {}
    assert r.overall_score == r.tfidf_score > 0


def test_recommendation_thresholds():
    scorer = ResumeScorer()
    high = scorer.thresholds["high_match_threshold"]
    low = scorer.thresholds["similarity_threshold"]
    assert scorer.recommend(high) == "Strong match"
    assert scorer.recommend((high + low) / 2) == "Possible match"
    assert scorer.recommend(low - 0.01) == "Weak match"
