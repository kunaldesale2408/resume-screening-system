"""
Request and response models for the scoring API.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ResumeText(BaseModel):
    name: str = Field(..., examples=["jane_doe.pdf"])
    text: str = Field(..., min_length=1)


class TextScoreRequest(BaseModel):
    job_description: str = Field(..., min_length=20)
    resumes: List[ResumeText] = Field(..., min_length=1, max_length=200)


class JobSummary(BaseModel):
    required_skills: List[str]
    preferred_skills: List[str]
    min_years: Optional[float]
    education: Optional[str]
    requires_certification: bool


class ResumeResult(BaseModel):
    rank: int
    filename: str
    candidate_name: Optional[str]
    overall_score: float
    tfidf_score: float
    entity_score: float
    recommendation: str
    matched_skills: List[str]
    missing_skills: List[str]
    missing_preferred: List[str]
    matched_keywords: List[str]
    years_experience: Optional[float]
    education: Optional[str]
    component_scores: Dict[str, float]
    certifications: List[str]
    organizations: List[str]


class ScoreResponse(BaseModel):
    job: JobSummary
    results: List[ResumeResult]
    processing_ms: int


class HealthResponse(BaseModel):
    status: str
    version: str
    spacy_model: str
    nlp_model_loaded: bool
