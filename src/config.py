"""
Configuration management for the Resume Screening System.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    """

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    API_WORKERS: int = 4

    # Streamlit Configuration
    STREAMLIT_PORT: int = 8501
    STREAMLIT_LOGGER_LEVEL: str = "info"

    # Application Settings
    APP_NAME: str = "Resume Screening System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Data Paths
    DATA_PATH: Path = Path("./data")
    RAW_DATA_PATH: Path = Path("./data/raw")
    PROCESSED_DATA_PATH: Path = Path("./data/processed")
    MODELS_PATH: Path = Path("./models")
    LOGS_PATH: Path = Path("./logs")

    # NLP Models
    SPACY_MODEL: str = "en_core_web_sm"
    TFIDF_MAX_FEATURES: int = 5000
    TFIDF_MIN_DF: int = 2
    TFIDF_MAX_DF: float = 0.95
    TFIDF_NGRAM_RANGE: tuple = (1, 2)

    # Matching Engine
    TFIDF_WEIGHT: float = 0.6
    ENTITY_WEIGHT: float = 0.4
    SIMILARITY_THRESHOLD: float = 0.5
    CONFIDENCE_THRESHOLD: float = 0.6

    # Kaggle API
    KAGGLE_USERNAME: Optional[str] = None
    KAGGLE_KEY: Optional[str] = None

    # CORS Settings
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://localhost:8000",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 50000000  # 50MB
    ALLOWED_EXTENSIONS: list = ["pdf", "txt", "docx"]

    # Processing Settings
    BATCH_SIZE: int = 32
    NUM_WORKERS: int = 4
    TIMEOUT: int = 300

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **data):
        """Initialize settings and create necessary directories."""
        super().__init__(**data)
        self._create_directories()

    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        for path in [
            self.DATA_PATH,
            self.RAW_DATA_PATH,
            self.PROCESSED_DATA_PATH,
            self.MODELS_PATH,
            self.LOGS_PATH,
        ]:
            path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
