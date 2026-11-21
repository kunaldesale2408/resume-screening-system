"""
Scoring endpoints.

POST /score       multipart upload: resume files + job description (text or file)
POST /score/text  JSON: job description text + resume texts (easy to call from other services)
GET  /config      current weights and thresholds
"""

from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from src.api.schemas import ScoreResponse, TextScoreRequest
from src.api.services import get_scorer, score_files, score_texts
from src.config import settings
from src.preprocessing import SUPPORTED_EXTENSIONS, ExtractionError, extract_text

router = APIRouter(tags=["Scoring"])

MAX_FILES = 200


async def _read_upload(upload: UploadFile) -> bytes:
    ext = Path(upload.filename or "").suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"{upload.filename}: unsupported file type. Use PDF, DOCX or TXT.",
        )
    data = await upload.read(settings.MAX_UPLOAD_SIZE + 1)
    if len(data) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"{upload.filename}: file is larger than {settings.MAX_UPLOAD_SIZE // 1_000_000} MB.",
        )
    return data


@router.post("/score", response_model=ScoreResponse)
async def score_uploads(
    resumes: List[UploadFile] = File(..., description="Resume files (PDF, DOCX or TXT)"),
    job_description: Optional[str] = Form(None, description="Job description text"),
    jd_file: Optional[UploadFile] = File(None, description="Or: job description file"),
):
    """Score and rank uploaded resumes against a job description."""
    if len(resumes) > MAX_FILES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Send at most {MAX_FILES} resumes per request.")

    try:
        if jd_file is not None and jd_file.filename:
            job_description = extract_text(await _read_upload(jd_file), jd_file.filename)
        if not job_description or len(job_description.strip()) < 20:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Provide a job description of at least 20 characters, as text or as a file.",
            )
        files = [(r.filename or f"resume_{i}", await _read_upload(r)) for i, r in enumerate(resumes, 1)]
        return score_files(job_description, files)
    except ExtractionError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.post("/score/text", response_model=ScoreResponse)
def score_text(request: TextScoreRequest):
    """Score resumes supplied as plain text (no file upload needed)."""
    return score_texts(request.job_description, [(r.name, r.text) for r in request.resumes])


@router.get("/config")
def get_config():
    """Weights and thresholds currently used by the matching engine."""
    scorer = get_scorer()
    return {
        "scoring_weights": scorer.score_weights,
        "entity_matching_weights": scorer.entity_weights,
        "thresholds": scorer.thresholds,
    }
