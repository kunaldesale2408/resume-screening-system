"""
Resume-to-job matching and scoring.

Each resume gets two scores, which are blended into one overall score:

1. TF-IDF similarity (lexical): cosine similarity between the TF-IDF vectors
   of the resume and the job description. It rewards resumes that use the
   same distinctive vocabulary as the job.

2. Entity match (structured): how well the resume meets the requirements
   the job states explicitly:
     - skills         share of the job's skill requirements the resume meets
                      ("FastAPI, Flask, or Django" is met by any one of them;
                      "a plus" skills count half)
     - experience     years on the resume vs. years the job asks for
     - education      degree level vs. the level the job asks for
     - certification  whether the resume lists one, if the job mentions any
   Only requirements the job actually states are scored; their weights are
   re-normalised so a job with no education requirement isn't penalised.

overall = w_tfidf * tfidf + w_entity * entity   (weights in config/features_config.json)

Note on TF-IDF: the IDF part is fitted on the batch being scored (the job
plus all uploaded resumes), so a resume's TF-IDF score can shift slightly
when other resumes are added. Rankings within a batch are what it is for.
"""

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.feature_engineering import (
    JobProfile,
    ResumeProfile,
    build_job_profile,
    build_resume_profile,
    group_label,
)

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "features_config.json"

# Below this many documents, min_df/max_df filters would throw away most
# terms (with 2 documents, max_df=0.95 drops every word they share).
_MIN_DOCS_FOR_DF_FILTERS = 20

# How much a "nice to have" skill counts compared with a required one.
_PREFERRED_WEIGHT = 0.5


def _identity(tokens):
    return tokens


@dataclass
class MatchResult:
    filename: str
    overall_score: float
    tfidf_score: float
    entity_score: float
    recommendation: str
    candidate_name: Optional[str]
    matched_skills: List[str]
    missing_skills: List[str]
    matched_keywords: List[str]
    years_experience: Optional[float]
    education: Optional[str]
    missing_preferred: List[str] = field(default_factory=list)
    component_scores: Dict[str, float] = field(default_factory=dict)
    certifications: List[str] = field(default_factory=list)
    organizations: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class ResumeScorer:
    """Scores and ranks resumes against one job description."""

    def __init__(self, config_path: Path = CONFIG_PATH):
        with open(config_path, encoding="utf-8") as fh:
            cfg = json.load(fh)
        self.tfidf_params = cfg["tfidf_params"]
        self.entity_weights = cfg["entity_matching_weights"]
        self.score_weights = cfg["scoring_weights"]
        self.thresholds = cfg["thresholds"]

    # ------------------------------------------------------------ public API

    def score_texts(
        self, job_text: str, resumes: Sequence[Tuple[str, str]]
    ) -> Tuple[JobProfile, List[MatchResult]]:
        """
        Convenience wrapper: build profiles from raw text, then score.

        Args:
            job_text: Job description text.
            resumes: (name, text) pairs.
        """
        job = build_job_profile(job_text)
        profiles = [build_resume_profile(text, name=name) for name, text in resumes]
        return job, self.score(job, profiles)

    def score(self, job: JobProfile, resumes: Sequence[ResumeProfile]) -> List[MatchResult]:
        """Return one MatchResult per resume, best match first."""
        if not resumes:
            return []
        tfidf_scores, keywords = self._tfidf_scores(job, resumes)

        results = []
        for resume, tfidf_score, kw in zip(resumes, tfidf_scores, keywords):
            entity_score, components = self._entity_score(job, resume)
            if components:
                overall = (
                    self.score_weights["tfidf_similarity"] * tfidf_score
                    + self.score_weights["entity_matching"] * entity_score
                )
            else:  # the job states no structured requirements at all
                overall = tfidf_score
            results.append(
                MatchResult(
                    filename=resume.name,
                    overall_score=round(float(overall), 4),
                    tfidf_score=round(float(tfidf_score), 4),
                    entity_score=round(float(entity_score), 4),
                    recommendation=self.recommend(overall),
                    candidate_name=resume.candidate_name,
                    matched_skills=sorted(job.skills & resume.skills, key=str.lower),
                    missing_skills=[group_label(g) for g in job.required_groups if not g & resume.skills],
                    missing_preferred=[group_label(g) for g in job.preferred_groups if not g & resume.skills],
                    matched_keywords=kw,
                    years_experience=resume.years_experience,
                    education=resume.education,
                    component_scores={k: round(v, 4) for k, v in components.items()},
                    certifications=resume.certifications,
                    organizations=resume.organizations,
                )
            )
        results.sort(key=lambda r: r.overall_score, reverse=True)
        return results

    def recommend(self, overall: float) -> str:
        if overall >= self.thresholds["high_match_threshold"]:
            return "Strong match"
        if overall >= self.thresholds["similarity_threshold"]:
            return "Possible match"
        return "Weak match"

    # -------------------------------------------------------------- TF-IDF

    def _vectorizer(self, n_docs: int) -> TfidfVectorizer:
        use_filters = n_docs >= _MIN_DOCS_FOR_DF_FILTERS
        return TfidfVectorizer(
            tokenizer=_identity,      # input is already a list of lemmas
            preprocessor=_identity,
            token_pattern=None,
            lowercase=False,
            ngram_range=tuple(self.tfidf_params.get("ngram_range", (1, 2))),
            max_features=self.tfidf_params.get("max_features"),
            min_df=self.tfidf_params.get("min_df", 1) if use_filters else 1,
            max_df=self.tfidf_params.get("max_df", 1.0) if use_filters else 1.0,
            sublinear_tf=True,        # 10 mentions != 10x as relevant
        )

    def _tfidf_scores(
        self, job: JobProfile, resumes: Sequence[ResumeProfile]
    ) -> Tuple[np.ndarray, List[List[str]]]:
        docs = [job.tokens] + [r.tokens for r in resumes]
        if not any(docs[0]) or not any(len(d) for d in docs[1:]):
            return np.zeros(len(resumes)), [[] for _ in resumes]

        vectorizer = self._vectorizer(len(docs))
        matrix = vectorizer.fit_transform(docs)
        job_vec, resume_vecs = matrix[0], matrix[1:]
        scores = cosine_similarity(resume_vecs, job_vec).ravel()

        # Keywords that contributed most to each resume's similarity.
        terms = vectorizer.get_feature_names_out()
        keywords = []
        job_dense = job_vec.toarray().ravel()
        for i in range(resume_vecs.shape[0]):
            contribution = resume_vecs[i].toarray().ravel() * job_dense
            top = np.argsort(contribution)[::-1][:25]
            kw = [
                terms[j] for j in top
                if contribution[j] > 0 and not terms[j].startswith("skill_") and "skill_" not in terms[j]
            ]
            keywords.append(kw[:10])
        return scores, keywords

    # -------------------------------------------------------- entity match

    def _entity_score(
        self, job: JobProfile, resume: ResumeProfile
    ) -> Tuple[float, Dict[str, float]]:
        components: Dict[str, float] = {}

        # Required skill groups count fully, preferred ("a plus") ones half.
        # A group is met when the resume has any one of its skills.
        denominator = len(job.required_groups) + _PREFERRED_WEIGHT * len(job.preferred_groups)
        if denominator:
            met_required = sum(1 for g in job.required_groups if g & resume.skills)
            met_preferred = sum(1 for g in job.preferred_groups if g & resume.skills)
            components["skills"] = (met_required + _PREFERRED_WEIGHT * met_preferred) / denominator

        if job.min_years:  # None or 0 means no real requirement
            if resume.years_experience is None:
                components["experience"] = 0.5  # unknown: neither reward nor punish fully
            else:
                components["experience"] = min(1.0, resume.years_experience / job.min_years)

        if job.education_level:
            gap = job.education_level - resume.education_level
            components["education"] = 1.0 if gap <= 0 else (0.5 if gap == 1 and resume.education_level else 0.0)

        if job.requires_certification:
            components["certifications"] = 1.0 if resume.certifications else 0.0

        if not components:
            return 0.0, components
        total_weight = sum(self.entity_weights[k] for k in components)
        score = sum(self.entity_weights[k] * v for k, v in components.items()) / total_weight
        return score, components


def rank_texts(job_text: str, resumes: Sequence[Tuple[str, str]]) -> List[dict]:
    """One-call helper used by scripts: returns results as plain dicts."""
    start = time.perf_counter()
    _, results = ResumeScorer().score_texts(job_text, resumes)
    elapsed = time.perf_counter() - start
    out = [r.to_dict() for r in results]
    for r in out:
        r["batch_seconds"] = round(elapsed, 3)
    return out
