"""
Scorer module for Resume Screening System.

Combines similarity and entity matching scores for final resume matching.
"""

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np

from src.matching.entity_matcher import EntityMatcher
from src.matching.similarity_calculator import SimilarityCalculator

logger = logging.getLogger(__name__)


class Scorer:
    """
    Scores resume-to-JD matches by combining multiple similarity metrics.
    """

    def __init__(
        self,
        tfidf_weight: float = 0.6,
        entity_weight: float = 0.4,
        similarity_threshold: float = 0.5,
        confidence_threshold: float = 0.6,
    ):
        """
        Initialize scorer.

        Args:
            tfidf_weight: Weight for TF-IDF similarity (0-1)
            entity_weight: Weight for entity matching (0-1)
            similarity_threshold: Minimum score to consider a match
            confidence_threshold: Minimum score for high confidence
        """
        self.tfidf_weight = tfidf_weight
        self.entity_weight = entity_weight
        self.similarity_threshold = similarity_threshold
        self.confidence_threshold = confidence_threshold

        self.similarity_calc = SimilarityCalculator()
        self.entity_matcher = EntityMatcher()

    def score_resume_jd_pair(
        self,
        resume_tfidf: np.ndarray,
        jd_tfidf: np.ndarray,
        resume_entities: Dict,
        jd_entities: Dict,
    ) -> Dict:
        """
        Score a resume-JD pair.

        Args:
            resume_tfidf: TF-IDF vector for resume
            jd_tfidf: TF-IDF vector for JD
            resume_entities: Extracted entities from resume
            jd_entities: Extracted entities from JD

        Returns:
            dict: Scoring details
        """
        # TF-IDF similarity
        tfidf_similarity = self.similarity_calc.cosine_similarity(
            resume_tfidf, jd_tfidf
        )

        # Entity matching
        entity_scores = self.entity_matcher.calculate_entity_match_score(
            resume_entities, jd_entities
        )
        entity_match_score = self.entity_matcher.calculate_weighted_score(
            entity_scores
        )

        # Combined score
        combined_score = (
            tfidf_similarity * self.tfidf_weight
            + entity_match_score * self.entity_weight
        )

        # Normalize to 0-100
        final_score = combined_score * 100

        # Determine confidence
        confidence = "high" if final_score >= self.confidence_threshold * 100 else "medium" if final_score >= self.similarity_threshold * 100 else "low"

        return {
            "score": round(final_score, 2),
            "confidence": confidence,
            "tfidf_similarity": round(tfidf_similarity * 100, 2),
            "entity_match_score": round(entity_match_score * 100, 2),
            "entity_breakdown": {
                k: round(v * 100, 2) for k, v in entity_scores.items()
            },
            "meets_threshold": final_score >= self.similarity_threshold * 100,
        }

    def score_multiple_resumes(
        self,
        resumes_data: List[Dict],
        jd_data: Dict,
        sort_by: str = "score",
        descending: bool = True,
    ) -> List[Dict]:
        """
        Score multiple resumes against a JD.

        Args:
            resumes_data: List of resume data dicts with tfidf and entities
            jd_data: Job description data dict with tfidf and entities
            sort_by: Field to sort by ('score', 'confidence')
            descending: Sort in descending order

        Returns:
            list: Sorted list of scored resumes
        """
        results = []

        for resume in resumes_data:
            score_data = self.score_resume_jd_pair(
                resume["tfidf"],
                jd_data["tfidf"],
                resume["entities"],
                jd_data["entities"],
            )

            result = {
                "resume_id": resume.get("id", "unknown"),
                "resume_name": resume.get("name", "Unknown"),
                **score_data,
            }
            results.append(result)

        # Sort results
        results = sorted(
            results,
            key=lambda x: x[sort_by],
            reverse=descending,
        )

        return results

    def get_top_matches(
        self,
        resumes_data: List[Dict],
        jd_data: Dict,
        top_n: int = 10,
        min_score: Optional[float] = None,
    ) -> List[Dict]:
        """
        Get top N matching resumes.

        Args:
            resumes_data: List of resume data
            jd_data: Job description data
            top_n: Number of top results to return
            min_score: Minimum score threshold (0-100)

        Returns:
            list: Top matching resumes
        """
        if min_score is None:
            min_score = self.similarity_threshold * 100

        all_scores = self.score_multiple_resumes(resumes_data, jd_data)

        # Filter by minimum score
        filtered = [r for r in all_scores if r["score"] >= min_score]

        return filtered[:top_n]

    def set_weights(self, tfidf_weight: float, entity_weight: float) -> None:
        """
        Update scoring weights.

        Args:
            tfidf_weight: Weight for TF-IDF (0-1)
            entity_weight: Weight for entity matching (0-1)
        """
        total = tfidf_weight + entity_weight
        self.tfidf_weight = tfidf_weight / total
        self.entity_weight = entity_weight / total
        logger.info(f"Updated weights: TF-IDF={self.tfidf_weight:.2%}, Entity={self.entity_weight:.2%}")


if __name__ == "__main__":
    # Example usage
    import json

    scorer = Scorer(tfidf_weight=0.6, entity_weight=0.4)

    # Mock resume and JD data
    resume_tfidf = np.random.rand(5000)
    jd_tfidf = np.random.rand(5000)

    resume_entities = {
        "skills": {"programming": ["python"], "ml_tools": ["tensorflow"]},
        "experience_level": 5,
        "education": ["bachelor"],
        "organizations": ["Tech Company"],
    }

    jd_entities = {
        "skills": {"programming": ["python"], "ml_tools": ["tensorflow"]},
        "experience_level": 5,
        "education": ["bachelor"],
        "organizations": [],
    }

    score = scorer.score_resume_jd_pair(
        resume_tfidf, jd_tfidf, resume_entities, jd_entities
    )

    print("Scoring Result:")
    print(json.dumps(score, indent=2))
