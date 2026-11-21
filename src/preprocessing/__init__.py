"""
Preprocessing module for text extraction and cleaning.
"""

from src.preprocessing.cleaner import lemmatize, lemmatize_doc, normalize
from src.preprocessing.extractor import (
    SUPPORTED_EXTENSIONS,
    ExtractionError,
    extract_text,
)

__all__ = [
    "extract_text",
    "ExtractionError",
    "SUPPORTED_EXTENSIONS",
    "normalize",
    "lemmatize",
    "lemmatize_doc",
]
