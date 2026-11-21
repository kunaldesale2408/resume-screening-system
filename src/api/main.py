"""
FastAPI application.

Run locally:   uvicorn src.api.main:app --reload --port 8000
Interactive docs: http://localhost:8000/docs
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import scoring_router
from src.api.schemas import HealthResponse
from src.api.services import get_scorer
from src.config import settings
from src.nlp import get_nlp, has_statistical_model

logging.basicConfig(level=settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load spaCy and the scoring config once at start-up, not on the first request.
    get_nlp()
    get_scorer()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Scores and ranks resumes against a job description using TF-IDF "
    "similarity plus skill, experience and education matching.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.include_router(scoring_router)


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        spacy_model=settings.SPACY_MODEL,
        nlp_model_loaded=has_statistical_model(),
    )
