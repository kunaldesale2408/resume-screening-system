"""
How the Streamlit app gets scores.

If the API_URL environment variable is set (docker-compose sets it to
http://backend:8000), resumes are sent to the FastAPI backend. Otherwise
the same scoring service runs inside the Streamlit process, so the app
also works on its own with `streamlit run`.
"""

import os
from typing import List, Tuple


class ScoringError(RuntimeError):
    """A readable error to show in the UI."""


def score(job_description: str, files: List[Tuple[str, bytes]]) -> dict:
    api_url = os.getenv("API_URL", "").rstrip("/")
    if api_url:
        return _score_via_api(api_url, job_description, files)

    from src.api.services import score_files
    from src.preprocessing import ExtractionError

    try:
        return score_files(job_description, files)
    except ExtractionError as exc:
        raise ScoringError(str(exc)) from exc


def _score_via_api(api_url: str, job_description: str, files: List[Tuple[str, bytes]]) -> dict:
    import requests

    try:
        response = requests.post(
            f"{api_url}/score",
            data={"job_description": job_description},
            files=[("resumes", (name, data)) for name, data in files],
            timeout=300,
        )
    except requests.RequestException as exc:
        raise ScoringError(f"Could not reach the scoring API at {api_url}: {exc}") from exc
    if response.status_code != 200:
        try:
            detail = response.json().get("detail")
        except ValueError:
            detail = response.text[:200]
        raise ScoringError(f"Scoring API error ({response.status_code}): {detail}")
    return response.json()
