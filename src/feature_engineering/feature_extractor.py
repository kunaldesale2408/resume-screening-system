"""
Feature extraction and combination module for Resume Screening System.

Combines TF-IDF vectors with entity extraction for comprehensive feature representation.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.preprocessing import StandardScaler

from src.config import settings
from src.feature_engineering.spacy_processor import SpacyProcessor, get_entity_overlap
from src.feature_engineering.tfidf_vectorizer import TFIDFVectorizer

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    Extracts and combines TF-IDF and entity-based features.
    """

    def __init__(
        self,
        tfidf_params: Optional[Dict] = None,
        entity_weights: Optional[Dict] = None,
        use_standardization: bool = True,
    ):
        """
        Initialize feature extractor.

        Args:
            tfidf_params: TF-IDF configuration parameters
            entity_weights: Weights for different entity types
            use_standardization: Whether to standardize features
        """
        # Default TF-IDF parameters
        if tfidf_params is None:
            tfidf_params = {
                "max_features": 5000,
                "min_df": 2,
                "max_df": 0.95,
                "ngram_range": (1, 2),
            }

        # Default entity weights
        if entity_weights is None:
            entity_weights = {
                "skills": 0.4,
                "experience": 0.3,
                "education": 0.2,
                "certifications": 0.1,
            }

        self.tfidf_params = tfidf_params
        self.entity_weights = entity_weights
        self.use_standardization = use_standardization

        self.tfidf_vectorizer = TFIDFVectorizer(**tfidf_params)
        self.spacy_processor = SpacyProcessor()
        self.scaler = StandardScaler() if use_standardization else None
        self.is_fitted = False

    def fit_tfidf(self, documents: List[str]) -> None:
        """
        Fit TF-IDF vectorizer on documents.

        Args:
            documents: List of text documents
        """
        logger.info(f"Fitting TF-IDF on {len(documents)} documents...")
        self.tfidf_vectorizer.fit(documents)

    def extract_tfidf_features(self, text: str) -> np.ndarray:
        """
        Extract TF-IDF features from text.

        Args:
            text: Input text

        Returns:
            TF-IDF feature vector
        """
        if not self.tfidf_vectorizer.is_fitted:
            logger.error("TF-IDF vectorizer not fitted")
            return np.array([])

        vector = self.tfidf_vectorizer.transform([text])
        return vector.toarray().flatten()

    def extract_entity_features(self, text: str) -> Dict[str, any]:
        """
        Extract entity-based features from text.

        Args:
            text: Input text

        Returns:
            Dictionary of entity features
        """
        return self.spacy_processor.extract_all_entities(text)

    def calculate_entity_score(
        self, resume_entities: Dict, jd_entities: Dict
    ) -> Dict[str, float]:
        """
        Calculate entity matching scores between resume and JD.

        Args:
            resume_entities: Entities from resume
            jd_entities: Entities from job description

        Returns:
            Dictionary of entity match scores
        """
        overlap = get_entity_overlap(resume_entities, jd_entities)

        # Apply weights
        weighted_scores = {}
        for entity_type, score in overlap.items():
            weight = self.entity_weights.get(entity_type, 0.1)
            weighted_scores[entity_type] = score * weight

        return weighted_scores

    def combine_features(
        self,
        tfidf_vector: np.ndarray,
        entity_scores: Dict[str, float],
        tfidf_weight: float = 0.6,
        entity_weight: float = 0.4,
    ) -> np.ndarray:
        """
        Combine TF-IDF and entity features.

        Args:
            tfidf_vector: TF-IDF feature vector
            entity_scores: Entity matching scores
            tfidf_weight: Weight for TF-IDF features (0-1)
            entity_weight: Weight for entity features (0-1)

        Returns:
            Combined feature vector
        """
        # Normalize weights
        total_weight = tfidf_weight + entity_weight
        tfidf_weight /= total_weight
        entity_weight /= total_weight

        # TF-IDF component
        tfidf_component = np.mean(tfidf_vector) * tfidf_weight if len(tfidf_vector) > 0 else 0

        # Entity component
        entity_scores_array = np.array(list(entity_scores.values()))
        entity_component = np.mean(entity_scores_array) * entity_weight if len(entity_scores_array) > 0 else 0

        # Combined vector
        combined = np.array([tfidf_component, entity_component])

        return combined

    def extract_all_features(
        self, resume_text: str, jd_text: str
    ) -> Dict:
        """
        Extract all features from resume and JD.

        Args:
            resume_text: Resume text
            jd_text: Job description text

        Returns:
            Dictionary containing all extracted features
        """
        logger.info("Extracting all features...")

        # Extract entities
        resume_entities = self.extract_entity_features(resume_text)
        jd_entities = self.extract_entity_features(jd_text)

        # Extract TF-IDF
        resume_tfidf = self.extract_tfidf_features(resume_text)
        jd_tfidf = self.extract_tfidf_features(jd_text)

        # Calculate entity scores
        entity_scores = self.calculate_entity_score(resume_entities, jd_entities)

        # Combine features
        combined_features = self.combine_features(resume_tfidf, entity_scores)

        return {
            "resume_entities": resume_entities,
            "jd_entities": jd_entities,
            "resume_tfidf_stats": {
                "mean": float(np.mean(resume_tfidf)),
                "max": float(np.max(resume_tfidf)),
                "nonzero": int(np.count_nonzero(resume_tfidf)),
            },
            "jd_tfidf_stats": {
                "mean": float(np.mean(jd_tfidf)),
                "max": float(np.max(jd_tfidf)),
                "nonzero": int(np.count_nonzero(jd_tfidf)),
            },
            "entity_scores": entity_scores,
            "combined_features": combined_features.tolist(),
        }

    def save_configuration(self, filepath: str) -> bool:
        """
        Save feature extractor configuration.

        Args:
            filepath: Path to save configuration

        Returns:
            bool: True if successful
        """
        try:
            config = {
                "tfidf_params": self.tfidf_params,
                "entity_weights": self.entity_weights,
                "use_standardization": self.use_standardization,
            }

            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "w") as f:
                json.dump(config, f, indent=2)

            logger.info(f"Configuration saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            return False

    def load_configuration(self, filepath: str) -> bool:
        """
        Load feature extractor configuration.

        Args:
            filepath: Path to load configuration

        Returns:
            bool: True if successful
        """
        try:
            filepath = Path(filepath)

            if not filepath.exists():
                logger.error(f"Configuration file not found: {filepath}")
                return False

            with open(filepath, "r") as f:
                config = json.load(f)

            self.tfidf_params = config.get("tfidf_params", self.tfidf_params)
            self.entity_weights = config.get("entity_weights", self.entity_weights)
            self.use_standardization = config.get("use_standardization", self.use_standardization)

            logger.info(f"Configuration loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            return False


if __name__ == "__main__":
    # Example usage
    resume_text = """
    John Doe - Senior Python Developer
    5+ years of experience with Python, FastAPI, and Machine Learning.
    Skills: Python, Django, FastAPI, TensorFlow, scikit-learn, Docker, Git
    Education: BS Computer Science
    """

    jd_text = """
    Senior Python Developer
    Required: 5+ years Python, FastAPI, REST API
    Machine Learning background preferred
    Skills: Python, FastAPI, TensorFlow, Docker
    Education: Bachelor's degree in Computer Science
    """

    # Create feature extractor
    extractor = FeatureExtractor()

    # Fit TF-IDF on combined documents
    extractor.fit_tfidf([resume_text, jd_text])

    # Extract all features
    features = extractor.extract_all_features(resume_text, jd_text)

    print("Extracted Features:")
    print(json.dumps(features, indent=2))

    # Save configuration
    extractor.save_configuration("config/feature_extractor_config.json")
