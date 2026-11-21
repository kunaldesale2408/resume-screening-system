"""
Text extraction from uploaded resume and job description files.

Supported formats: PDF, DOCX and plain text. For PDFs several libraries are
tried in order, because each one handles different PDF layouts better:

1. pdfplumber  - best at keeping the reading order of multi-column resumes
2. PyMuPDF     - fast and robust, used if pdfplumber is not installed
3. PyPDF2      - pure Python fallback
4. Tesseract OCR (via pdf2image) - only when the PDF has no text layer,
   i.e. it is a scanned image
"""

import io
import logging
from pathlib import Path

log = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

# A PDF page with fewer characters than this is treated as "no text layer".
_MIN_CHARS_PER_PAGE = 20


class ExtractionError(ValueError):
    """Raised when a file cannot be read or contains no usable text."""


def extract_text(data: bytes, filename: str) -> str:
    """
    Extract plain text from a file's bytes.

    Args:
        data: Raw file content.
        filename: Original file name; its extension selects the parser.

    Returns:
        The extracted text (never empty).

    Raises:
        ExtractionError: unsupported type, unreadable file, or no text found.
    """
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ExtractionError(
            f"{filename}: unsupported file type '{ext or 'none'}'. "
            f"Use one of: {', '.join(sorted(SUPPORTED_EXTENSIONS))}."
        )
    if not data:
        raise ExtractionError(f"{filename}: the file is empty.")

    if ext == ".pdf":
        text = _extract_pdf(data, filename)
    elif ext == ".docx":
        text = _extract_docx(data, filename)
    else:
        text = _decode_text(data)

    text = text.strip()
    if not text:
        raise ExtractionError(f"{filename}: no readable text was found in the file.")
    return text


def _decode_text(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-16", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="ignore")


def _extract_docx(data: bytes, filename: str) -> str:
    try:
        import docx  # python-docx
    except ImportError as exc:
        raise ExtractionError(f"{filename}: python-docx is not installed.") from exc
    try:
        document = docx.Document(io.BytesIO(data))
    except Exception as exc:  # corrupt or non-docx content
        raise ExtractionError(f"{filename}: could not open the Word file ({exc}).") from exc

    parts = [p.text for p in document.paragraphs]
    # Many resume templates put skills and dates inside tables.
    for table in document.tables:
        for row in table.rows:
            parts.append(" | ".join(cell.text for cell in row.cells))
    return "\n".join(parts)


def _extract_pdf(data: bytes, filename: str) -> str:
    errors = []
    for name, extractor in (
        ("pdfplumber", _pdf_with_pdfplumber),
        ("pymupdf", _pdf_with_pymupdf),
        ("pypdf2", _pdf_with_pypdf2),
    ):
        try:
            text, n_pages = extractor(data)
        except ImportError:
            continue
        except Exception as exc:  # try the next library
            errors.append(f"{name}: {exc}")
            continue
        if len(text.strip()) >= _MIN_CHARS_PER_PAGE * max(n_pages, 1) * 0.5:
            log.debug("Extracted %s with %s", filename, name)
            return text
        # Text layer missing or nearly empty: maybe a scanned PDF.
        ocr_text = _pdf_with_ocr(data)
        return ocr_text if len(ocr_text.strip()) > len(text.strip()) else text

    detail = "; ".join(errors) if errors else "no PDF library is installed"
    raise ExtractionError(f"{filename}: could not read the PDF ({detail}).")


def _pdf_with_pdfplumber(data: bytes):
    import pdfplumber

    with pdfplumber.open(io.BytesIO(data)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages), len(pages)


def _pdf_with_pymupdf(data: bytes):
    import pymupdf

    with pymupdf.open(stream=data, filetype="pdf") as doc:
        pages = [page.get_text() for page in doc]
    return "\n".join(pages), len(pages)


def _pdf_with_pypdf2(data: bytes):
    from PyPDF2 import PdfReader

    reader = PdfReader(io.BytesIO(data))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages), len(pages)


def _pdf_with_ocr(data: bytes) -> str:
    """OCR for scanned PDFs. Returns '' when OCR tools are not available."""
    try:
        import pytesseract
        from pdf2image import convert_from_bytes
    except ImportError:
        return ""
    try:
        images = convert_from_bytes(data, dpi=200)
        return "\n".join(pytesseract.image_to_string(img) for img in images)
    except Exception as exc:  # poppler or tesseract binary missing
        log.warning("OCR failed: %s", exc)
        return ""
