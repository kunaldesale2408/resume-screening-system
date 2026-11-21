"""
Feature engineering module for NLP feature extraction.

``build_resume_profile`` and ``build_job_profile`` run spaCy once per
document and collect everything the matcher needs: lemmas for TF-IDF,
canonical skills, years of experience, education level, certifications,
and named entities.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Set

from src.feature_engineering import entities
from src.feature_engineering.skills import (
    SkillGroup,
    extract_skills,
    group_label,
    job_skill_requirements,
    skill_token,
)
from src.nlp import get_nlp
from src.preprocessing import lemmatize_doc, normalize


@dataclass
class ResumeProfile:
    name: str
    text: str
    tokens: List[str]
    skills: Set[str]
    years_experience: Optional[float]
    education_level: int
    certifications: List[str] = field(default_factory=list)
    organizations: List[str] = field(default_factory=list)
    candidate_name: Optional[str] = None

    @property
    def education(self) -> Optional[str]:
        return entities.EDUCATION_LEVELS[self.education_level]


@dataclass
class JobProfile:
    text: str
    tokens: List[str]
    required_groups: List[SkillGroup]
    preferred_groups: List[SkillGroup]
    min_years: Optional[float]
    education_level: int
    requires_certification: bool

    @property
    def skills(self) -> Set[str]:
        """Every skill the job mentions (required or preferred)."""
        return set().union(*self.required_groups, *self.preferred_groups)

    @property
    def education(self) -> Optional[str]:
        return entities.EDUCATION_LEVELS[self.education_level]


def _tfidf_tokens(doc, skills: Set[str]) -> List[str]:
    """Lemmas plus one normalised token per skill (so aliases match in TF-IDF)."""
    return lemmatize_doc(doc) + [skill_token(s) for s in sorted(skills)]


def build_resume_profile(raw_text: str, name: str = "resume") -> ResumeProfile:
    text = normalize(raw_text)
    doc = get_nlp()(text)
    sections = entities.split_sections(text)
    skills = extract_skills(text)
    return ResumeProfile(
        name=name,
        text=text,
        tokens=_tfidf_tokens(doc, skills),
        skills=skills,
        years_experience=entities.resume_years(text, sections),
        education_level=entities.resume_education(sections.get("education") or text),
        certifications=entities.certifications(text, sections),
        organizations=entities.organizations(doc),
        candidate_name=entities.candidate_name(doc, text),
    )


def build_job_profile(raw_text: str) -> JobProfile:
    text = normalize(raw_text)
    doc = get_nlp()(text)
    required, preferred = job_skill_requirements(text)
    return JobProfile(
        text=text,
        tokens=_tfidf_tokens(doc, extract_skills(text)),
        required_groups=required,
        preferred_groups=preferred,
        min_years=entities.required_years(text),
        education_level=entities.required_education(text),
        requires_certification=entities.requires_certification(text),
    )


__all__ = [
    "ResumeProfile",
    "JobProfile",
    "build_resume_profile",
    "build_job_profile",
    "extract_skills",
    "group_label",
    "SkillGroup",
]
