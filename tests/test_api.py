"""Tests for the FastAPI backend."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_config(client):
    body = client.get("/config").json()
    assert set(body) == {"scoring_weights", "entity_matching_weights", "thresholds"}


def test_score_text_ranks_resumes(client, sample_resume, sample_jd):
    response = client.post(
        "/score/text",
        json={
            "job_description": sample_jd,
            "resumes": [
                {"name": "chef.txt", "text": "Head chef. Menu planning and food safety."},
                {"name": "john.txt", "text": sample_resume},
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert [r["filename"] for r in body["results"]] == ["john.txt", "chef.txt"]
    assert body["results"][0]["rank"] == 1
    assert "Python" in body["job"]["required_skills"]


def test_score_file_upload(client, sample_resume, sample_jd):
    files = [("resumes", ("john.txt", sample_resume.encode("utf-8"), "text/plain"))]
    pymupdf = pytest.importorskip("pymupdf")
    doc = pymupdf.open()
    doc.new_page().insert_text((72, 72), "Chef with menu planning experience.")
    files.append(("resumes", ("chef.pdf", doc.tobytes(), "application/pdf")))

    response = client.post("/score", data={"job_description": sample_jd}, files=files)
    assert response.status_code == 200
    assert response.json()["results"][0]["filename"] == "john.txt"


def test_job_description_as_file(client, sample_resume, sample_jd):
    response = client.post(
        "/score",
        files=[
            ("resumes", ("john.txt", sample_resume.encode("utf-8"), "text/plain")),
            ("jd_file", ("jd.txt", sample_jd.encode("utf-8"), "text/plain")),
        ],
    )
    assert response.status_code == 200


def test_unsupported_file_type(client, sample_jd):
    response = client.post(
        "/score",
        data={"job_description": sample_jd},
        files=[("resumes", ("cv.exe", b"binary", "application/octet-stream"))],
    )
    assert response.status_code == 400
    assert "unsupported file type" in response.json()["detail"]


def test_unreadable_pdf_names_the_file(client, sample_jd):
    response = client.post(
        "/score",
        data={"job_description": sample_jd},
        files=[("resumes", ("broken.pdf", b"not a pdf", "application/pdf"))],
    )
    assert response.status_code == 400
    assert "broken.pdf" in response.json()["detail"]


def test_missing_job_description(client, sample_resume):
    response = client.post(
        "/score",
        files=[("resumes", ("john.txt", sample_resume.encode("utf-8"), "text/plain"))],
    )
    assert response.status_code == 400
