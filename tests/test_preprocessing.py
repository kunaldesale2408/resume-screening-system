"""
Tests for preprocessing module.
"""

import pytest
from pathlib import Path

from src.preprocessing.text_cleaner import TextCleaner, clean_text, tokenize_text


class TestTextCleaner:
    """Tests for TextCleaner class."""

    def test_clean_basic(self):
        """Test basic text cleaning."""
        cleaner = TextCleaner(remove_stopwords=False)
        text = "Hello WORLD!!! This is a TEST."
        cleaned = cleaner.clean(text)
        assert cleaned.islower()
        assert "!!!" not in cleaned

    def test_remove_urls(self):
        """Test URL removal."""
        cleaner = TextCleaner()
        text = "Visit https://example.com for more info."
        cleaned = cleaner.clean(text)
        assert "https" not in cleaned
        assert "example.com" not in cleaned

    def test_remove_emails(self):
        """Test email removal."""
        cleaner = TextCleaner()
        text = "Contact me at john@example.com for details."
        cleaned = cleaner.clean(text)
        assert "@" not in cleaned
        assert "john" in cleaned

    def test_remove_phone_numbers(self):
        """Test phone number removal."""
        cleaner = TextCleaner()
        text = "Call me at (555) 123-4567 or 555-987-6543."
        cleaned = cleaner.clean(text)
        assert "555" not in cleaned
        assert "123" not in cleaned

    def test_tokenize(self, sample_resume):
        """Test tokenization."""
        cleaner = TextCleaner(remove_stopwords=False)
        tokens = cleaner.tokenize(sample_resume)
        assert len(tokens) > 0
        assert isinstance(tokens, list)
        assert all(isinstance(t, str) for t in tokens)

    def test_remove_stopwords(self):
        """Test stopword removal."""
        cleaner = TextCleaner(remove_stopwords=True)
        tokens = ["the", "python", "and", "developer", "is", "a", "test"]
        filtered = cleaner.remove_stopwords(tokens)
        assert "the" not in filtered
        assert "and" not in filtered
        assert "python" in filtered
        assert "developer" in filtered

    def test_process_full_pipeline(self, sample_resume):
        """Test full processing pipeline."""
        cleaner = TextCleaner(remove_stopwords=True)
        tokens = cleaner.process_full_pipeline(sample_resume)
        assert len(tokens) > 0
        assert all(len(t) >= 2 for t in tokens)

    def test_clean_empty_string(self):
        """Test cleaning empty string."""
        cleaner = TextCleaner()
        assert cleaner.clean("") == ""
        assert cleaner.clean(None) == ""

    def test_clean_special_characters(self):
        """Test special character removal."""
        cleaner = TextCleaner()
        text = "Test@#$%^&*()Text"
        cleaned = cleaner.clean(text)
        assert "@" not in cleaned
        assert "#" not in cleaned
        assert "test" in cleaned.lower()


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_clean_text_function(self, sample_resume):
        """Test clean_text convenience function."""
        cleaned = clean_text(sample_resume)
        assert isinstance(cleaned, str)
        assert len(cleaned) > 0

    def test_tokenize_text_function(self, sample_resume):
        """Test tokenize_text convenience function."""
        tokens = tokenize_text(sample_resume)
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert all(isinstance(t, str) for t in tokens)
