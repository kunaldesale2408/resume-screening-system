"""
Tests for matching engine module.
"""

import json
import pytest
import numpy as np

from src.matching.entity_matcher import EntityMatcher
from src.matching.scorer import Scorer
from src.matching.similarity_calculator import SimilarityCalculator
from src.matching.validator import Validator


class TestSimilarityCalculator:
    """Tests for SimilarityCalculator class."""

    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        calc = SimilarityCalculator()
        v1 = np.array([1, 0, 1])
        v2 = np.array([1, 0, 1])
        sim = calc.cosine_similarity(v1, v2)
        assert sim == pytest.approx(1.0, abs=0.01)

    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity with orthogonal vectors."""
        calc = SimilarityCalculator()
        v1 = np.array([1, 0, 0])
        v2 = np.array([0, 1, 0])
        sim = calc.cosine_similarity(v1, v2)
        assert sim == pytest.approx(0.0, abs=0.01)

    def test_euclidean_distance(self):
        """Test Euclidean distance calculation."""
        calc = SimilarityCalculator()
        v1 = np.array([0, 0, 0])
        v2 = np.array([1, 0, 0])
        dist = calc.euclidean_distance(v1, v2)
        assert dist == pytest.approx(1.0, abs=0.01)

    def test_manhattan_distance(self):
        """Test Manhattan distance calculation."""
        calc = SimilarityCalculator()
        v1 = np.array([0, 0, 0])
        v2 = np.array([1, 1, 1])
        dist = calc.manhattan_distance(v1, v2)
        assert dist == 3.0

    def test_jaccard_similarity(self):
        """Test Jaccard similarity calculation."""
        calc = SimilarityCalculator()
        set1 = {"a", "b", "c"}
        set2 = {"b", "c", "d"}
        sim = calc.jaccard_similarity(set1, set2)
        assert sim == pytest.approx(0.5, abs=0.01)

    def test_compare_vectors(self):
        """Test comparing vectors with multiple methods."""
        calc = SimilarityCalculator()
        v1 = np.array([1, 0, 1])
        v2 = np.array([1, 1, 0])
        scores = calc.compare_vectors(v1, v2, methods=["cosine", "euclidean"])
        assert "cosine_similarity" in scores
        assert "euclidean_distance" in scores


class TestEntityMatcher:
    """Tests for EntityMatcher class."""

    def test_initialization(self):
        """Test entity matcher initialization."""
        matcher = EntityMatcher()
        assert matcher.weights is not None
        assert matcher.weights["skills"] == 0.4

    def test_match_skills_perfect(self):
        """Test perfect skill match."""
        matcher = EntityMatcher()
        resume_skills = {"programming": ["python", "java"]}
        jd_skills = {"programming": ["python"]}
        score = matcher.match_skills(resume_skills, jd_skills)
        assert score == 1.0

    def test_match_skills_partial(self):
        """Test partial skill match."""
        matcher = EntityMatcher()
        resume_skills = {"programming": ["python"]}
        jd_skills = {"programming": ["python", "java"]}
        score = matcher.match_skills(resume_skills, jd_skills)
        assert score == 0.5

    def test_match_experience_sufficient(self):
        """Test sufficient experience match."""
        matcher = EntityMatcher()
        score = matcher.match_experience(5, 3)
        assert score == 1.0

    def test_match_experience_insufficient(self):
        """Test insufficient experience match."""
        matcher = EntityMatcher()
        score = matcher.match_experience(2, 5)
        assert score == pytest.approx(0.4, abs=0.01)

    def test_match_education_perfect(self):
        """Test perfect education match."""
        matcher = EntityMatcher()
        resume_edu = ["bachelor", "computer science"]
        jd_edu = ["bachelor"]
        score = matcher.match_education(resume_edu, jd_edu)
        assert score == 1.0


class TestScorer:
    """Tests for Scorer class."""

    def test_initialization(self):
        """Test scorer initialization."""
        scorer = Scorer(tfidf_weight=0.6, entity_weight=0.4)
        assert scorer.tfidf_weight == 0.6
        assert scorer.entity_weight == 0.4

    def test_score_resume_jd_pair(self):
        """Test scoring a resume-JD pair."""
        scorer = Scorer()
        resume_tfidf = np.random.rand(100)
        jd_tfidf = np.random.rand(100)
        resume_entities = {
            "skills": {"programming": ["python"]},
            "experience_level": 5,
            "education": ["bachelor"],
            "organizations": [],
        }
        jd_entities = {
            "skills": {"programming": ["python"]},
            "experience_level": 5,
            "education": ["bachelor"],
            "organizations": [],
        }

        score = scorer.score_resume_jd_pair(
            resume_tfidf, jd_tfidf, resume_entities, jd_entities
        )
        assert "score" in score
        assert "confidence" in score
        assert 0 <= score["score"] <= 100


class TestValidator:
    """Tests for Validator class."""

    def test_initialization(self):
        """Test validator initialization."""
        validator = Validator(threshold=0.5)
        assert validator.threshold == 0.5

    def test_validate_on_labeled_set(self):
        """Test validation on labeled set."""
        validator = Validator(threshold=0.5)
        predictions = [0.9, 0.8, 0.3, 0.2, 0.7]
        ground_truth = [1, 1, 0, 0, 1]
        metrics = validator.validate_on_labeled_set(predictions, ground_truth)
        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics

    def test_validate_multiple_thresholds(self):
        """Test validation at multiple thresholds."""
        validator = Validator()
        predictions = [0.9, 0.8, 0.3, 0.2, 0.7]
        ground_truth = [1, 1, 0, 0, 1]
        results = validator.validate_multiple_thresholds(
            predictions, ground_truth, thresholds=[0.3, 0.5, 0.7]
        )
        assert len(results) == 3
        assert 0.3 in results
        assert 0.5 in results
        assert 0.7 in results

    def test_calculate_confusion_matrix(self):
        """Test confusion matrix calculation."""
        validator = Validator(threshold=0.5)
        predictions = [0.9, 0.8, 0.3, 0.2, 0.7]
        ground_truth = [1, 1, 0, 0, 1]
        cm = validator.calculate_confusion_matrix(predictions, ground_truth)
        assert cm.shape == (2, 2)
        assert cm[0, 0] + cm[0, 1] + cm[1, 0] + cm[1, 1] == len(predictions)
