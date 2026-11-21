"""Tests for text extraction and cleaning."""

import io

import pytest

from src.preprocessing import ExtractionError, extract_text, lemmatize, normalize


def test_extract_txt():
    assert extract_text("Python developer".encode("utf-8"), "cv.txt") == "Python developer"


def test_extract_docx_includes_tables():
    docx = pytest.importorskip("docx")
    document = docx.Document()
    document.add_paragraph("Jane Doe")
    table = document.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "Skills"
    table.rows[0].cells[1].text = "Python, SQL"
    buffer = io.BytesIO()
    document.save(buffer)

    text = extract_text(buffer.getvalue(), "cv.docx")
    assert "Jane Doe" in text
    assert "Python, SQL" in text


def test_extract_pdf():
    pymupdf = pytest.importorskip("pymupdf")
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Machine learning engineer with Python and SQL experience.")
    data = doc.tobytes()

    assert "Machine learning engineer" in extract_text(data, "cv.pdf")


def test_unsupported_extension():
    with pytest.raises(ExtractionError, match="unsupported file type"):
        extract_text(b"data", "cv.exe")


def test_empty_file():
    with pytest.raises(ExtractionError, match="empty"):
        extract_text(b"", "cv.txt")


def test_corrupt_pdf():
    with pytest.raises(ExtractionError):
        extract_text(b"this is not a pdf", "cv.pdf")


def test_normalize_removes_contact_details_but_keeps_dates():
    text = "Jane | jane@mail.com | +91 98765 43210 | www.jane.dev\nAnalyst (2018 - 2021)"
    clean = normalize(text)
    assert "jane@mail.com" not in clean
    assert "98765" not in clean
    assert "www.jane.dev" not in clean
    assert "2018 - 2021" in clean


def test_lemmatize_drops_stop_and_boilerplate_words():
    lemmas = lemmatize("Developed data pipelines with 3 years of experience in the team")
    assert "develop" in lemmas
    assert "data" in lemmas  # not spaCy's "datum"
    for dropped in ("with", "the", "experience", "year", "3"):
        assert dropped not in lemmas
