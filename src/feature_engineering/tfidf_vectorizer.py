"""
TF-IDF Vectorization module for Resume Screening System.

Creates numerical representations of text documents using TF-IDF algorithm.
"""

import json
import logging
import pickle
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from src.config import settings

logger = logging.getLogger(__name__)


class TFIDFVectorizer:
    """
    Manages TF-IDF vectorization of text documents.
    """

    def __init__(
        self,
        max_features: int = 5000,
        min_df: int = 2,
        max_df: float = 0.95,
        ngram_range: Tuple[int, int] = (1, 2),
        lowercase: bool = True,
        stop_words: str = "english",
    ):
        """
        Initialize TF-IDF vectorizer.

        Args:
            max_features: Maximum number of features to extract
            min_df: Minimum document frequency
            max_df: Maximum document frequency (0-1)
            ngram_range: N-gram range (1,2) for unigrams and bigrams
            lowercase: Convert text to lowercase
            stop_words: Stop words to use ('english' or list)
        """
        self.max_features = max_features
        self.min_df = min_df
        self.max_df = max_df
        self.ngram_range = ngram_range
        self.lowercase = lowercase
        self.stop_words = stop_words

        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            min_df=min_df,
            max_df=max_df,
            ngram_range=ngram_range,
            lowercase=lowercase,
            stop_words=stop_words,
            norm="l2",
            use_idf=True,
        )
        self.is_fitted = False

    def fit(self, documents: List[str]) -> None:
        """
        Fit the TF-IDF vectorizer on documents.

        Args:
            documents: List of text documents
        """
        logger.info(f"Fitting TF-IDF vectorizer on {len(documents)} documents...")

        try:
            self.vectorizer.fit(documents)
            self.is_fitted = True
            logger.info(f"Vectorizer fitted. Features: {len(self.vectorizer.get_feature_names_out())}")
        except Exception as e:
            logger.error(f"Failed to fit vectorizer: {str(e)}")
            raise

    def transform(self, documents: List[str]) -> np.ndarray:
        """
        Transform documents to TF-IDF vectors.

        Args:
            documents: List of text documents

        Returns:
            Sparse matrix of TF-IDF vectors
        """
        if not self.is_fitted:
            logger.error("Vectorizer not fitted. Call fit() first.")
            raise ValueError("Vectorizer not fitted")

        logger.debug(f"Transforming {len(documents)} documents...")
        vectors = self.vectorizer.transform(documents)
        return vectors

    def fit_transform(self, documents: List[str]) -> np.ndarray:
        """
        Fit and transform documents in one step.

        Args:
            documents: List of text documents

        Returns:
            Sparse matrix of TF-IDF vectors
        """
        logger.info(f"Fitting and transforming {len(documents)} documents...")

        try:
            vectors = self.vectorizer.fit_transform(documents)
            self.is_fitted = True
            logger.info(f"Fit-transform complete. Vector shape: {vectors.shape}")
            return vectors
        except Exception as e:
            logger.error(f"Failed to fit-transform: {str(e)}")
            raise

    def get_feature_names(self) -> List[str]:
        """
        Get list of feature names (terms).

        Returns:
            List of feature names
        """
        if not self.is_fitted:
            logger.warning("Vectorizer not fitted. Returning empty list.")
            return []

        return list(self.vectorizer.get_feature_names_out())

    def get_top_features(self, vector: np.ndarray, n: int = 10) -> List[Tuple[str, float]]:
        """
        Get top N features from a TF-IDF vector.

        Args:
            vector: TF-IDF vector (sparse or dense)
            n: Number of top features to return

        Returns:
            List of (feature_name, score) tuples
        """
        if not self.is_fitted:
            logger.error("Vectorizer not fitted")
            return []

        feature_names = self.get_feature_names()

        # Convert sparse matrix to dense if needed
        if hasattr(vector, "toarray"):
            vector_dense = vector.toarray().flatten()
        else:
            vector_dense = np.array(vector).flatten()

        # Get top indices
        top_indices = np.argsort(vector_dense)[-n:][::-1]

        # Build result list
        top_features = [
            (feature_names[i], float(vector_dense[i])) for i in top_indices if vector_dense[i] > 0
        ]

        return top_features

    def save(self, filepath: str) -> bool:
        """
        Save fitted vectorizer to file.

        Args:
            filepath: Path to save vectorizer

        Returns:
            bool: True if successful
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "wb") as f:
                pickle.dump(self.vectorizer, f)

            logger.info(f"Vectorizer saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save vectorizer: {str(e)}")
            return False

    def load(self, filepath: str) -> bool:
        """
        Load fitted vectorizer from file.

        Args:
            filepath: Path to load vectorizer

        Returns:
            bool: True if successful
        """
        try:
            filepath = Path(filepath)

            if not filepath.exists():
                logger.error(f"Vectorizer file not found: {filepath}")
                return False

            with open(filepath, "rb") as f:
                self.vectorizer = pickle.load(f)

            self.is_fitted = True
            logger.info(f"Vectorizer loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load vectorizer: {str(e)}")
            return False

    def get_vocabulary_size(self) -> int:
        """
        Get size of vocabulary.

        Returns:
            int: Number of features in vocabulary
        """
        if not self.is_fitted:
            return 0

        return len(self.vectorizer.get_feature_names_out())

    def get_stats(self) -> dict:
        """
        Get vectorizer statistics.

        Returns:
            dict: Statistics dictionary
        """
        return {
            "is_fitted": self.is_fitted,
            "vocabulary_size": self.get_vocabulary_size(),
            "max_features": self.max_features,
            "min_df": self.min_df,
            "max_df": self.max_df,
            "ngram_range": self.ngram_range,
        }


if __name__ == "__main__":
    # Example usage
    documents = [
        "Python developer with 5 years experience",
        "Machine learning engineer with TensorFlow",
        "Senior Python developer with FastAPI",
        "ML engineer with PyTorch and deep learning",
    ]

    vectorizer = TFIDFVectorizer(
        max_features=100, min_df=1, max_df=0.9, ngram_range=(1, 2)
    )

    # Fit and transform
    vectors = vectorizer.fit_transform(documents)
    print(f"Vector shape: {vectors.shape}")
    print(f"Vocabulary size: {vectorizer.get_vocabulary_size()}")

    # Get top features from first document
    top_features = vectorizer.get_top_features(vectors[0], n=5)
    print(f"\nTop features: {top_features}")

    # Save vectorizer
    vectorizer.save("models/tfidf_vectorizer.pkl")
