"""
Scoring service: the one place that turns files or text into ranked results.

Both the FastAPI routes and the Streamlit app call this, so they always
produce identical scores.
"""

import time
from functools import lru_cache
from typing import List, Sequence, Tuple

from src.feature_engineering import build_job_profile, build_resume_profile, group_label
from src.matching import ResumeScorer
from src.preprocessing import extract_text


@lru_cache(maxsize=1)
def get_scorer() -> ResumeScorer:
    return ResumeScorer()


def score_texts(job_description: str, resumes: Sequence[Tuple[str, str]]) -> dict:
    """
    Score resumes given as (name, text) pairs.

    Returns a dict shaped like ``schemas.ScoreResponse``.
    """
    start = time.perf_counter()
    job = build_job_profile(job_description)
    profiles = [build_resume_profile(text, name=name) for name, text in resumes]
    results = get_scorer().score(job, profiles)

    return {
        "job": {
            "required_skills": [group_label(g) for g in job.required_groups],
            "preferred_skills": [group_label(g) for g in job.preferred_groups],
            "min_years": job.min_years,
            "education": job.education,
            "requires_certification": job.requires_certification,
        },
        "results": [{"rank": i, **r.to_dict()} for i, r in enumerate(results, start=1)],
        "processing_ms": int((time.perf_counter() - start) * 1000),
    }


def score_files(job_description: str, files: Sequence[Tuple[str, bytes]]) -> dict:
    """
    Score uploaded files given as (filename, bytes) pairs.

    Raises:
        ExtractionError: if any file can't be read. The message names the file.
    """
    texts: List[Tuple[str, str]] = [(name, extract_text(data, name)) for name, data in files]
    return score_texts(job_description, texts)
