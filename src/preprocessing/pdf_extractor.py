"""
PDF text extraction module for Resume Screening System.

Handles extraction of text from PDF files with OCR fallback for scanned documents.
"""

import logging
from pathlib import Path
from typing import Optional

try:
    import pytesseract
    from pdf2image import convert_from_path
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False
    logging.warning("Tesseract dependencies not installed. OCR will be skipped.")

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    logging.warning("pdfplumber not installed. PDF text extraction may fail.")

try:
    from PyPDF2 import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

logger = logging.getLogger(__name__)


class PDFExtractor:
    """
    Extracts text from PDF files with multiple fallback methods.
    """

    def __init__(self, use_ocr: bool = True, tesseract_cmd: Optional[str] = None):
        """
        Initialize PDF extractor.

        Args:
            use_ocr: Whether to use OCR for scanned PDFs
            tesseract_cmd: Path to tesseract executable (if not in PATH)
        """
        self.use_ocr = use_ocr and HAS_TESSERACT
        if tesseract_cmd:
            pytesseract.pytesseract.pytesseract_cmd = tesseract_cmd

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF file with multiple fallback methods.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            str: Extracted text
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return ""

        if not pdf_path.suffix.lower() == ".pdf":
            logger.error(f"File is not a PDF: {pdf_path}")
            return ""

        # Try pdfplumber first (fastest for digital PDFs)
        if HAS_PDFPLUMBER:
            text = self._extract_with_pdfplumber(pdf_path)
            if text.strip():
                logger.debug(f"Successfully extracted text using pdfplumber from {pdf_path.name}")
                return text

        # Fallback to PyPDF2
        if HAS_PYPDF:
            text = self._extract_with_pypdf(pdf_path)
            if text.strip():
                logger.debug(f"Successfully extracted text using PyPDF2 from {pdf_path.name}")
                return text

        # Fallback to OCR for scanned PDFs
        if self.use_ocr:
            try:
                text = self._extract_with_ocr(pdf_path)
                if text.strip():
                    logger.debug(f"Successfully extracted text using OCR from {pdf_path.name}")
                    return text
            except Exception as e:
                logger.warning(f"OCR extraction failed: {str(e)}")

        logger.error(f"All extraction methods failed for {pdf_path.name}")
        return ""

    @staticmethod
    def _extract_with_pdfplumber(pdf_path: Path) -> str:
        """
        Extract text using pdfplumber.

        Args:
            pdf_path: Path to PDF file

        Returns:
            str: Extracted text
        """
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            logger.debug(f"pdfplumber extraction failed: {str(e)}")
            return ""

    @staticmethod
    def _extract_with_pypdf(pdf_path: Path) -> str:
        """
        Extract text using PyPDF2.

        Args:
            pdf_path: Path to PDF file

        Returns:
            str: Extracted text
        """
        try:
            text = ""
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
        except Exception as e:
            logger.debug(f"PyPDF2 extraction failed: {str(e)}")
            return ""

    @staticmethod
    def _extract_with_ocr(pdf_path: Path, dpi: int = 200) -> str:
        """
        Extract text using OCR (Tesseract) for scanned PDFs.

        Args:
            pdf_path: Path to PDF file
            dpi: Resolution for image conversion

        Returns:
            str: Extracted text
        """
        try:
            logger.info(f"Running OCR on {pdf_path.name} at {dpi} DPI...")
            images = convert_from_path(pdf_path, dpi=dpi)
            text = ""
            for page_num, image in enumerate(images, 1):
                logger.debug(f"Processing page {page_num}/{len(images)}")
                page_text = pytesseract.image_to_string(image)
                if page_text:
                    text += page_text + "\n"
            return text
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return ""

    def extract_from_multiple(self, pdf_paths: list) -> dict:
        """
        Extract text from multiple PDF files.

        Args:
            pdf_paths: List of PDF file paths

        Returns:
            dict: Mapping of file names to extracted text
        """
        results = {}
        total = len(pdf_paths)

        for idx, pdf_path in enumerate(pdf_paths, 1):
            logger.info(f"Processing file {idx}/{total}: {Path(pdf_path).name}")
            text = self.extract_text(pdf_path)
            results[Path(pdf_path).name] = text

        logger.info(f"Extraction complete: {len(results)} files processed")
        return results


def extract_resume_text(pdf_path: str, use_ocr: bool = True) -> str:
    """
    Convenience function to extract text from a resume PDF.

    Args:
        pdf_path: Path to the PDF file
        use_ocr: Whether to use OCR fallback

    Returns:
        str: Extracted text
    """
    extractor = PDFExtractor(use_ocr=use_ocr)
    return extractor.extract_text(pdf_path)


if __name__ == "__main__":
    # Example usage
    extractor = PDFExtractor(use_ocr=True)

    # Extract from single PDF
    sample_pdf = "path/to/resume.pdf"
    if Path(sample_pdf).exists():
        text = extractor.extract_text(sample_pdf)
        print(f"Extracted {len(text)} characters")
    else:
        print(f"Sample PDF not found: {sample_pdf}")
