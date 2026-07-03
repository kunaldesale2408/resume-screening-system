"""
Entity matching module for Resume Screening System.

Matches entities between resume and job description.
"""

import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class EntityMatcher:
    """
    Matches entities between resume and job description.
    """

    def __init__(
        self,
        weights: Dict[str, float] = None,
    ):
        """
        Initialize entity matcher.

        Args:
            weights: Weights for different entity types
        """
        if weights is None:
            weights = {
                "skills": 0.4,
                "experience": 0.3,
                "education": 0.2,
                "organizations": 0.1,
            }

        self.weights = weights

    def match_skills(
        self,
        resume_skills: Dict[str, List[str]],
        jd_skills: Dict[str, List[str]],
    ) -> float:
        """
        Calculate skill match score.

        Args:
            resume_skills: Skills from resume (by category)
            jd_skills: Required skills from JD (by category)

        Returns:
            float: Skill match score (0-1)
        """
        try:
            resume_skill_set = set()
            for skills_list in resume_skills.values():
                resume_skill_set.update(skills_list)

            jd_skill_set = set()
            for skills_list in jd_skills.values():
                jd_skill_set.update(skills_list)

            if not jd_skill_set:
                return 0.0

            matched = len(resume_skill_set & jd_skill_set)
            total = len(jd_skill_set)

            return matched / total
        except Exception as e:
            logger.error(f"Skill matching failed: {str(e)}")
            return 0.0

    def match_experience(
        self,
        resume_experience: int,
        jd_experience: int,
    ) -> float:
        """
        Calculate experience match score.

        Args:
            resume_experience: Years of experience from resume
            jd_experience: Required years of experience from JD

        Returns:
            float: Experience match score (0-1)
        """
        try:
            if jd_experience is None or jd_experience == 0:
                return 1.0

            if resume_experience is None:
                return 0.0

            # If candidate has more or equal experience, full score
            if resume_experience >= jd_experience:
                return 1.0
            else:
                # Partial score based on percentage of required experience
                return resume_experience / jd_experience
        except Exception as e:
            logger.error(f"Experience matching failed: {str(e)}")
            return 0.0

    def match_education(
        self,
        resume_education: List[str],
        jd_education: List[str],
    ) -> float:
        """
        Calculate education match score.

        Args:
            resume_education: Education from resume
            jd_education: Required education from JD

        Returns:
            float: Education match score (0-1)
        """
        try:
            resume_edu_set = set(resume_education) if resume_education else set()
            jd_edu_set = set(jd_education) if jd_education else set()

            if not jd_edu_set:
                return 1.0

            matched = len(resume_edu_set & jd_edu_set)
            total = len(jd_edu_set)

            return matched / total if total > 0 else 0.0
        except Exception as e:
            logger.error(f"Education matching failed: {str(e)}")
            return 0.0

    def match_organizations(
        self,
        resume_orgs: List[str],
        jd_orgs: List[str],
    ) -> float:
        """
        Calculate organization/company match score.

        Args:
            resume_orgs: Companies in resume
            jd_orgs: Required companies from JD

        Returns:
            float: Organization match score (0-1)
        """
        try:
            resume_org_set = set([org.lower() for org in resume_orgs])
            jd_org_set = set([org.lower() for org in jd_orgs])

            if not jd_org_set:
                return 0.5  # No specific company requirement

            matched = len(resume_org_set & jd_org_set)
            total = len(jd_org_set)

            return matched / total if total > 0 else 0.0
        except Exception as e:
            logger.error(f"Organization matching failed: {str(e)}")
            return 0.0

    def calculate_entity_match_score(
        self,
        resume_entities: Dict,
        jd_entities: Dict,
    ) -> Dict[str, float]:
        """
        Calculate overall entity match scores.

        Args:
            resume_entities: All entities extracted from resume
            jd_entities: All entities extracted from JD

        Returns:
            dict: Match scores for each entity type
        """
        scores = {}

        # Skills matching
        resume_skills = resume_entities.get("skills", {})
        jd_skills = jd_entities.get("skills", {})
        scores["skills"] = self.match_skills(resume_skills, jd_skills)

        # Experience matching
        resume_exp = resume_entities.get("experience_level")
        jd_exp = jd_entities.get("experience_level")
        scores["experience"] = self.match_experience(resume_exp, jd_exp)

        # Education matching
        resume_edu = resume_entities.get("education", [])
        jd_edu = jd_entities.get("education", [])
        scores["education"] = self.match_education(resume_edu, jd_edu)

        # Organization matching
        resume_orgs = resume_entities.get("organizations", [])
        jd_orgs = jd_entities.get("organizations", [])
        scores["organizations"] = self.match_organizations(resume_orgs, jd_orgs)

        return scores

    def calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """
        Calculate weighted entity match score.

        Args:
            scores: Individual entity match scores

        Returns:
            float: Weighted score (0-1)
        """
        try:
            weighted_sum = 0.0
            total_weight = 0.0

            for entity_type, score in scores.items():
                weight = self.weights.get(entity_type, 0.0)
                weighted_sum += score * weight
                total_weight += weight

            if total_weight == 0:
                return 0.0

            return weighted_sum / total_weight
        except Exception as e:
            logger.error(f"Weighted score calculation failed: {str(e)}")
            return 0.0


if __name__ == "__main__":
    # Example usage
    matcher = EntityMatcher()

    resume_entities = {
        "skills": {"programming": ["python", "java"], "ml_tools": ["tensorflow"]},
        "experience_level": 5,
        "education": ["bachelor", "computer science"],
        "organizations": ["Tech Company", "StartUp"],
    }

    jd_entities = {
        "skills": {"programming": ["python"], "ml_tools": ["tensorflow", "pytorch"]},
        "experience_level": 5,
        "education": ["bachelor"],
        "organizations": [],
    }

    scores = matcher.calculate_entity_match_score(resume_entities, jd_entities)
    print(f"Entity scores: {scores}")

    weighted = matcher.calculate_weighted_score(scores)
    print(f"Weighted score: {weighted:.2%}")
