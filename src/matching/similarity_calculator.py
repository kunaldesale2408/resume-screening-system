"""
Similarity calculation module for Resume Screening System.

Calculates cosine similarity between resume and job description vectors.
"""

import logging
from typing import Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class SimilarityCalculator:
    """
    Calculates similarity scores between documents.
    """

    @staticmethod
    def cosine_similarity(vector1: np.ndarray, vector2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vector1: First vector (TF-IDF or other)
            vector2: Second vector (TF-IDF or other)

        Returns:
            float: Similarity score (0-1)
        """
        try:
            # Reshape if needed
            if vector1.ndim == 1:
                vector1 = vector1.reshape(1, -1)
            if vector2.ndim == 1:
                vector2 = vector2.reshape(1, -1)

            # Calculate cosine similarity
            similarity = cosine_similarity(vector1, vector2)[0, 0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {str(e)}")
            return 0.0

    @staticmethod
    def euclidean_distance(vector1: np.ndarray, vector2: np.ndarray) -> float:
        """
        Calculate Euclidean distance between two vectors.

        Args:
            vector1: First vector
            vector2: Second vector

        Returns:
            float: Euclidean distance
        """
        try:
            distance = np.linalg.norm(vector1 - vector2)
            return float(distance)
        except Exception as e:
            logger.error(f"Euclidean distance calculation failed: {str(e)}")
            return 0.0

    @staticmethod
    def manhattan_distance(vector1: np.ndarray, vector2: np.ndarray) -> float:
        """
        Calculate Manhattan distance between two vectors.

        Args:
            vector1: First vector
            vector2: Second vector

        Returns:
            float: Manhattan distance
        """
        try:
            distance = np.sum(np.abs(vector1 - vector2))
            return float(distance)
        except Exception as e:
            logger.error(f"Manhattan distance calculation failed: {str(e)}")
            return 0.0

    @staticmethod
    def jaccard_similarity(set1: set, set2: set) -> float:
        """
        Calculate Jaccard similarity between two sets.

        Args:
            set1: First set
            set2: Second set

        Returns:
            float: Jaccard similarity (0-1)
        """
        try:
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            if union == 0:
                return 0.0
            return intersection / union
        except Exception as e:
            logger.error(f"Jaccard similarity calculation failed: {str(e)}")
            return 0.0

    @staticmethod
    def compare_vectors(
        vector1: np.ndarray,
        vector2: np.ndarray,
        methods: list = None,
    ) -> dict:
        """
        Compare vectors using multiple similarity metrics.

        Args:
            vector1: First vector
            vector2: Second vector
            methods: List of methods to use ('cosine', 'euclidean', 'manhattan')

        Returns:
            dict: Dictionary of similarity scores
        """
        if methods is None:
            methods = ["cosine"]

        results = {}

        if "cosine" in methods:
            results["cosine_similarity"] = SimilarityCalculator.cosine_similarity(
                vector1, vector2
            )

        if "euclidean" in methods:
            results["euclidean_distance"] = SimilarityCalculator.euclidean_distance(
                vector1, vector2
            )

        if "manhattan" in methods:
            results["manhattan_distance"] = SimilarityCalculator.manhattan_distance(
                vector1, vector2
            )

        return results


if __name__ == "__main__":
    # Example usage
    v1 = np.array([1, 0, 1, 0, 1])
    v2 = np.array([1, 1, 0, 1, 0])

    calc = SimilarityCalculator()

    print(f"Cosine Similarity: {calc.cosine_similarity(v1, v2):.4f}")
    print(f"Euclidean Distance: {calc.euclidean_distance(v1, v2):.4f}")
    print(f"Manhattan Distance: {calc.manhattan_distance(v1, v2):.4f}")

    scores = calc.compare_vectors(
        v1, v2, methods=["cosine", "euclidean", "manhattan"]
    )
    print(f"\nAll metrics: {scores}")
