"""
Text cleaning and preprocessing module for Resume Screening System.

Handles tokenization, lowercasing, special character removal, and stopword removal.
"""

import logging
import re
from typing import List, Optional

import nltk

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)


class TextCleaner:
    """
    Cleans and preprocesses text data.
    """

    def __init__(self, remove_stopwords: bool = True, custom_stopwords: Optional[List[str]] = None):
        """
        Initialize text cleaner.

        Args:
            remove_stopwords: Whether to remove English stopwords
            custom_stopwords: List of additional stopwords to remove
        """
        self.remove_stopwords_flag = remove_stopwords
        self.stop_words = set(stopwords.words("english"))

        if custom_stopwords:
            self.stop_words.update(custom_stopwords)

        # Common domain-specific stopwords for resumes/JDs
        self.domain_stopwords = {
            "job",
            "position",
            "role",
            "experience",
            "required",
            "responsible",
            "company",
            "work",
            "team",
        }
        self.stop_words.update(self.domain_stopwords)

    def clean(self, text: str, lowercase: bool = True, remove_special: bool = True) -> str:
        """
        Clean text with multiple preprocessing steps.

        Args:
            text: Input text
            lowercase: Whether to convert to lowercase
            remove_special: Whether to remove special characters

        Returns:
            str: Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""

        # Remove URLs
        text = self._remove_urls(text)

        # Remove email addresses
        text = self._remove_emails(text)

        # Remove phone numbers
        text = self._remove_phone_numbers(text)

        # Convert to lowercase
        if lowercase:
            text = text.lower()

        # Remove special characters
        if remove_special:
            text = self._remove_special_characters(text)

        # Remove extra whitespace
        text = self._remove_extra_whitespace(text)

        return text.strip()

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.

        Args:
            text: Input text

        Returns:
            List of tokens
        """
        if not text or not isinstance(text, str):
            return []

        try:
            tokens = word_tokenize(text)
            return tokens
        except Exception as e:
            logger.error(f"Tokenization failed: {str(e)}")
            # Fallback to simple split
            return text.split()

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords from token list.

        Args:
            tokens: List of tokens

        Returns:
            List of tokens with stopwords removed
        """
        if not self.remove_stopwords_flag:
            return tokens

        return [token for token in tokens if token.lower() not in self.stop_words]

    def process_full_pipeline(
        self,
        text: str,
        remove_stopwords: bool = True,
        lowercase: bool = True,
        min_token_length: int = 2,
    ) -> List[str]:
        """
        Execute full text processing pipeline.

        Args:
            text: Input text
            remove_stopwords: Whether to remove stopwords
            lowercase: Whether to convert to lowercase
            min_token_length: Minimum token length to keep

        Returns:
            List of processed tokens
        """
        # Clean text
        cleaned = self.clean(text, lowercase=lowercase, remove_special=True)

        # Tokenize
        tokens = self.tokenize(cleaned)

        # Remove stopwords
        if remove_stopwords:
            tokens = self.remove_stopwords(tokens)

        # Filter by minimum length
        tokens = [t for t in tokens if len(t) >= min_token_length]

        return tokens

    @staticmethod
    def _remove_urls(text: str) -> str:
        """
        Remove URLs from text.

        Args:
            text: Input text

        Returns:
            str: Text with URLs removed
        """
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        return re.sub(url_pattern, "", text)

    @staticmethod
    def _remove_emails(text: str) -> str:
        """
        Remove email addresses from text.

        Args:
            text: Input text

        Returns:
            str: Text with emails removed
        """
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return re.sub(email_pattern, "", text)

    @staticmethod
    def _remove_phone_numbers(text: str) -> str:
        """
        Remove phone numbers from text.

        Args:
            text: Input text

        Returns:
            str: Text with phone numbers removed
        """
        phone_pattern = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|\+?1?\d{9,15}\b"
        return re.sub(phone_pattern, "", text)

    @staticmethod
    def _remove_special_characters(text: str) -> str:
        """
        Remove special characters, keeping alphanumeric and basic punctuation.

        Args:
            text: Input text

        Returns:
            str: Text with special characters removed
        """
        # Keep alphanumeric, spaces, hyphens, and common punctuation
        text = re.sub(r"[^a-zA-Z0-9\s\-+.()]", " ", text)
        return text

    @staticmethod
    def _remove_extra_whitespace(text: str) -> str:
        """
        Remove extra whitespace.

        Args:
            text: Input text

        Returns:
            str: Text with extra whitespace removed
        """
        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text)
        return text.strip()


def clean_text(text: str, remove_stopwords: bool = True) -> str:
    """
    Convenience function to clean text.

    Args:
        text: Input text
        remove_stopwords: Whether to remove stopwords

    Returns:
        str: Cleaned text
    """
    cleaner = TextCleaner(remove_stopwords=remove_stopwords)
    return cleaner.clean(text)


def tokenize_text(text: str, remove_stopwords: bool = True) -> List[str]:
    """
    Convenience function to tokenize text.

    Args:
        text: Input text
        remove_stopwords: Whether to remove stopwords

    Returns:
        List of tokens
    """
    cleaner = TextCleaner(remove_stopwords=remove_stopwords)
    return cleaner.process_full_pipeline(text)


if __name__ == "__main__":
    # Example usage
    cleaner = TextCleaner(remove_stopwords=True)

    sample_text = """
    John Doe - Senior Python Developer
    Email: john@example.com | Phone: (555) 123-4567
    Website: https://johndoe.com
    
    5+ years of experience with Python, FastAPI, and Machine Learning.
    Strong background in REST API development and cloud deployment.
    """

    print("Original text:")
    print(sample_text)

    print("\nCleaned text:")
    cleaned = cleaner.clean(sample_text)
    print(cleaned)

    print("\nTokens (without stopwords):")
    tokens = cleaner.process_full_pipeline(sample_text)
    print(tokens)
