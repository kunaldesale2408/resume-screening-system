"""
spaCy-based entity extraction module for Resume Screening System.

Extracts named entities and custom entities from resume and job description text.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set

import spacy
from spacy.matcher import PhraseMatcher

logger = logging.getLogger(__name__)

# Skill keywords for pattern matching
SKILL_KEYWORDS = {
    "programming": [
        "python",
        "java",
        "javascript",
        "c++",
        "c#",
        "ruby",
        "go",
        "rust",
        "php",
        "scala",
    ],
    "frameworks": [
        "fastapi",
        "django",
        "flask",
        "react",
        "vue",
        "angular",
        "node.js",
        "express",
        "spring",
    ],
    "ml_tools": [
        "tensorflow",
        "pytorch",
        "scikit-learn",
        "keras",
        "xgboost",
        "spacy",
        "nltk",
        "pandas",
        "numpy",
    ],
    "databases": [
        "sql",
        "postgresql",
        "mysql",
        "mongodb",
        "redis",
        "cassandra",
        "elasticsearch",
    ],
    "devops": [
        "docker",
        "kubernetes",
        "git",
        "jenkins",
        "aws",
        "gcp",
        "azure",
        "terraform",
    ],
}

EXPERIENCE_PATTERNS = ["years", "year experience", "+ years", "years of experience"]


class SpacyProcessor:
    """
    Processes text using spaCy for entity extraction.
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize spaCy processor.

        Args:
            model_name: Name of spaCy model to load
        """
        self.model_name = model_name
        self.nlp = None
        self.load_model()

    def load_model(self) -> bool:
        """
        Load spaCy model.

        Returns:
            bool: True if model loaded successfully
        """
        try:
            self.nlp = spacy.load(self.model_name)
            logger.info(f"Loaded spaCy model: {self.model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {str(e)}")
            logger.info(f"Try: python -m spacy download {self.model_name}")
            return False

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text.

        Args:
            text: Input text

        Returns:
            Dictionary of entity types to entity values
        """
        if not self.nlp:
            logger.error("spaCy model not loaded")
            return {}

        try:
            doc = self.nlp(text)
            entities = {}

            for ent in doc.ents:
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                entities[ent.label_].append(ent.text.lower())

            # Remove duplicates
            for key in entities:
                entities[key] = list(set(entities[key]))

            return entities
        except Exception as e:
            logger.error(f"Entity extraction failed: {str(e)}")
            return {}

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """
        Extract skill keywords from text using pattern matching.

        Args:
            text: Input text

        Returns:
            Dictionary of skill categories to skills found
        """
        text_lower = text.lower()
        skills_found = {}

        for category, keywords in SKILL_KEYWORDS.items():
            skills_found[category] = []
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    skills_found[category].append(keyword)

        # Remove empty categories
        skills_found = {k: v for k, v in skills_found.items() if v}

        return skills_found

    def extract_experience_level(self, text: str) -> Optional[int]:
        """
        Extract experience level (years) from text.

        Args:
            text: Input text

        Returns:
            int: Years of experience (if found), None otherwise
        """
        import re

        text_lower = text.lower()

        # Pattern: "5+ years" or "5 years" or "5 year"
        pattern = r"(\d+)\+?\s*(?:year|yr)s?"
        matches = re.findall(pattern, text_lower)

        if matches:
            # Return the maximum experience mentioned
            return max([int(m) for m in matches])

        return None

    def extract_education(self, text: str) -> List[str]:
        """
        Extract education level and degrees from text.

        Args:
            text: Input text

        Returns:
            List of education-related terms found
        """
        education_keywords = [
            "bachelor",
            "master",
            "phd",
            "b.s.",
            "m.s.",
            "b.a.",
            "m.a.",
            "degree",
            "diploma",
            "certification",
            "associate",
        ]

        text_lower = text.lower()
        education_found = []

        for keyword in education_keywords:
            if keyword in text_lower:
                education_found.append(keyword)

        return list(set(education_found))

    def extract_organizations(self, text: str) -> List[str]:
        """
        Extract organization names from text.

        Args:
            text: Input text

        Returns:
            List of organization names
        """
        if not self.nlp:
            return []

        try:
            doc = self.nlp(text)
            organizations = []

            for ent in doc.ents:
                if ent.label_ == "ORG":
                    organizations.append(ent.text)

            return list(set(organizations))
        except Exception as e:
            logger.error(f"Organization extraction failed: {str(e)}")
            return []

    def extract_all_entities(self, text: str) -> Dict:
        """
        Extract all types of entities from text.

        Args:
            text: Input text

        Returns:
            Dictionary containing all extracted entities
        """
        return {
            "named_entities": self.extract_entities(text),
            "skills": self.extract_skills(text),
            "experience_level": self.extract_experience_level(text),
            "education": self.extract_education(text),
            "organizations": self.extract_organizations(text),
        }


def get_entity_overlap(resume_entities: Dict, jd_entities: Dict) -> Dict[str, float]:
    """
    Calculate overlap between resume and JD entities.

    Args:
        resume_entities: Entities from resume
        jd_entities: Entities from job description

    Returns:
        Dictionary of overlap scores for each entity type
    """
    overlap = {}

    # Skills overlap
    resume_skills = set()
    for skills_list in resume_entities.get("skills", {}).values():
        resume_skills.update(skills_list)

    jd_skills = set()
    for skills_list in jd_entities.get("skills", {}).values():
        jd_skills.update(skills_list)

    if jd_skills:
        overlap["skills"] = len(resume_skills & jd_skills) / len(jd_skills)
    else:
        overlap["skills"] = 0.0

    # Experience overlap
    resume_exp = resume_entities.get("experience_level")
    jd_exp = jd_entities.get("experience_level")

    if jd_exp and resume_exp:
        overlap["experience"] = min(resume_exp / jd_exp, 1.0)
    else:
        overlap["experience"] = 0.0

    # Education overlap
    resume_edu = set(resume_entities.get("education", []))
    jd_edu = set(jd_entities.get("education", []))

    if jd_edu:
        overlap["education"] = len(resume_edu & jd_edu) / len(jd_edu)
    else:
        overlap["education"] = 0.0

    return overlap


if __name__ == "__main__":
    # Example usage
    processor = SpacyProcessor()

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

    print("Resume Entities:")
    resume_entities = processor.extract_all_entities(resume_text)
    print(json.dumps(resume_entities, indent=2))

    print("\nJD Entities:")
    jd_entities = processor.extract_all_entities(jd_text)
    print(json.dumps(jd_entities, indent=2))

    print("\nEntity Overlap:")
    overlap = get_entity_overlap(resume_entities, jd_entities)
    print(json.dumps(overlap, indent=2))
