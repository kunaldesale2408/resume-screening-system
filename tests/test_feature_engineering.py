"""
Tests for feature engineering module.
"""

import json
import pytest

from src.feature_engineering.feature_extractor import FeatureExtractor
from src.feature_engineering.spacy_processor import SpacyProcessor, get_entity_overlap
from src.feature_engineering.tfidf_vectorizer import TFIDFVectorizer


class TestTFIDFVectorizer:
    """Tests for TFIDFVectorizer class."""

    def test_initialization(self):
        """Test vectorizer initialization."""
        vectorizer = TFIDFVectorizer(max_features=1000)
        assert vectorizer.max_features == 1000
        assert not vectorizer.is_fitted

    def test_fit(self, sample_resume, sample_jd):
        """Test vectorizer fitting."""
        documents = [sample_resume, sample_jd]
        vectorizer = TFIDFVectorizer(max_features=500)
        vectorizer.fit(documents)
        assert vectorizer.is_fitted

    def test_transform(self, sample_resume, sample_jd):
        """Test text transformation."""
        documents = [sample_resume, sample_jd]
        vectorizer = TFIDFVectorizer(max_features=500)
        vectorizer.fit(documents)
        vectors = vectorizer.transform(documents)
        assert vectors.shape[0] == len(documents)

    def test_fit_transform(self, sample_resume, sample_jd):
        """Test fit and transform in one step."""
        documents = [sample_resume, sample_jd]
        vectorizer = TFIDFVectorizer(max_features=500)
        vectors = vectorizer.fit_transform(documents)
        assert vectorizer.is_fitted
        assert vectors.shape[0] == len(documents)

    def test_get_feature_names(self, sample_resume, sample_jd):
        """Test getting feature names."""
        documents = [sample_resume, sample_jd]
        vectorizer = TFIDFVectorizer(max_features=100)
        vectorizer.fit(documents)
        features = vectorizer.get_feature_names()
        assert len(features) > 0
        assert all(isinstance(f, str) for f in features)

    def test_get_top_features(self, sample_resume, sample_jd):
        """Test getting top features from vector."""
        documents = [sample_resume, sample_jd]
        vectorizer = TFIDFVectorizer(max_features=500)
        vectors = vectorizer.fit_transform(documents)
        top_features = vectorizer.get_top_features(vectors[0], n=5)
        assert len(top_features) <= 5
        assert all(isinstance(f, tuple) and len(f) == 2 for f in top_features)

    def test_vocabulary_size(self, sample_resume, sample_jd):
        """Test vocabulary size calculation."""
        documents = [sample_resume, sample_jd]
        vectorizer = TFIDFVectorizer(max_features=100)
        assert vectorizer.get_vocabulary_size() == 0
        vectorizer.fit(documents)
        assert vectorizer.get_vocabulary_size() > 0

    def test_get_stats(self, sample_resume, sample_jd):
        """Test getting vectorizer statistics."""
        documents = [sample_resume, sample_jd]
        vectorizer = TFIDFVectorizer(max_features=500)
        vectorizer.fit(documents)
        stats = vectorizer.get_stats()
        assert stats["is_fitted"] is True
        assert stats["vocabulary_size"] > 0


class TestSpacyProcessor:
    """Tests for SpacyProcessor class."""

    def test_initialization(self):
        """Test spaCy processor initialization."""
        processor = SpacyProcessor()
        assert processor.nlp is not None

    def test_extract_entities(self, sample_resume):
        """Test entity extraction."""
        processor = SpacyProcessor()
        entities = processor.extract_entities(sample_resume)
        assert isinstance(entities, dict)

    def test_extract_skills(self, sample_resume):
        """Test skill extraction."""
        processor = SpacyProcessor()
        skills = processor.extract_skills(sample_resume)
        assert isinstance(skills, dict)
        # Should find Python-related skills
        assert any("python" in str(v).lower() for v in skills.values())

    def test_extract_experience_level(self, sample_resume):
        """Test experience level extraction."""
        processor = SpacyProcessor()
        exp = processor.extract_experience_level(sample_resume)
        assert exp is not None
        assert exp > 0

    def test_extract_education(self, sample_resume):
        """Test education extraction."""
        processor = SpacyProcessor()
        education = processor.extract_education(sample_resume)
        assert isinstance(education, list)

    def test_extract_organizations(self, sample_resume):
        """Test organization extraction."""
        processor = SpacyProcessor()
        orgs = processor.extract_organizations(sample_resume)
        assert isinstance(orgs, list)

    def test_extract_all_entities(self, sample_resume):
        """Test extracting all entity types."""
        processor = SpacyProcessor()
        all_entities = processor.extract_all_entities(sample_resume)
        assert "named_entities" in all_entities
        assert "skills" in all_entities
        assert "experience_level" in all_entities
        assert "education" in all_entities
        assert "organizations" in all_entities


class TestEntityOverlap:
    """Tests for entity overlap calculation."""

    def test_get_entity_overlap(self, sample_resume, sample_jd):
        """Test entity overlap calculation."""
        processor = SpacyProcessor()
        resume_entities = processor.extract_all_entities(sample_resume)
        jd_entities = processor.extract_all_entities(sample_jd)

        overlap = get_entity_overlap(resume_entities, jd_entities)
        assert isinstance(overlap, dict)
        assert "skills" in overlap
        assert "experience" in overlap
        assert "education" in overlap


class TestFeatureExtractor:
    """Tests for FeatureExtractor class."""

    def test_initialization(self):
        """Test feature extractor initialization."""
        extractor = FeatureExtractor()
        assert extractor.tfidf_vectorizer is not None
        assert extractor.spacy_processor is not None

    def test_fit_tfidf(self, sample_resume, sample_jd):
        """Test TF-IDF fitting."""
        extractor = FeatureExtractor()
        documents = [sample_resume, sample_jd]
        extractor.fit_tfidf(documents)
        assert extractor.tfidf_vectorizer.is_fitted

    def test_extract_tfidf_features(self, sample_resume, sample_jd):
        """Test TF-IDF feature extraction."""
        extractor = FeatureExtractor()
        documents = [sample_resume, sample_jd]
        extractor.fit_tfidf(documents)
        features = extractor.extract_tfidf_features(sample_resume)
        assert len(features) > 0

    def test_extract_entity_features(self, sample_resume):
        """Test entity feature extraction."""
        extractor = FeatureExtractor()
        entities = extractor.extract_entity_features(sample_resume)
        assert isinstance(entities, dict)

    def test_extract_all_features(self, sample_resume, sample_jd):
        """Test extracting all features."""
        extractor = FeatureExtractor()
        documents = [sample_resume, sample_jd]
        extractor.fit_tfidf(documents)
        features = extractor.extract_all_features(sample_resume, sample_jd)
        assert "resume_entities" in features
        assert "jd_entities" in features
        assert "entity_scores" in features
        assert "combined_features" in features
