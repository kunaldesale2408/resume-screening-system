"""
Kaggle dataset loader for Resume Screening System.

Handles downloading and loading resume and job description datasets from Kaggle.
"""

import csv
import json
import logging
import os
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd

from src.config import settings

logger = logging.getLogger(__name__)


class KaggleDataLoader:
    """
    Loads and manages datasets from Kaggle.
    """

    def __init__(self):
        """Initialize the data loader."""
        self.raw_data_path = settings.RAW_DATA_PATH
        self.processed_data_path = settings.PROCESSED_DATA_PATH
        self.raw_data_path.mkdir(parents=True, exist_ok=True)
        self.processed_data_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def download_dataset(dataset_name: str, output_path: Optional[Path] = None) -> bool:
        """
        Download a dataset from Kaggle using kaggle CLI.

        Args:
            dataset_name: Kaggle dataset identifier (e.g., 'elnahas/resume-dataset')
            output_path: Path to save the dataset

        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            import kaggle

            if output_path is None:
                output_path = settings.RAW_DATA_PATH

            output_path.mkdir(parents=True, exist_ok=True)

            logger.info(f"Downloading dataset: {dataset_name}")
            kaggle.api.dataset_download_files(dataset_name, path=output_path, unzip=True)
            logger.info(f"Dataset downloaded successfully to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to download dataset: {str(e)}")
            logger.info("To use Kaggle download, ensure kaggle CLI is installed:")
            logger.info("  pip install kaggle")
            logger.info("  Configure credentials: ~/.kaggle/kaggle.json")
            return False

    def load_resumes_csv(
        self, filename: str = "resumes.csv", sample_size: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Load resume data from CSV file.

        Args:
            filename: Name of the CSV file
            sample_size: Optional number of samples to load

        Returns:
            pd.DataFrame: Resume dataframe
        """
        file_path = self.raw_data_path / filename

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return pd.DataFrame()

        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} resumes from {filename}")

            if sample_size:
                df = df.sample(n=min(sample_size, len(df)), random_state=42)
                logger.info(f"Sampled {len(df)} resumes")

            return df

        except Exception as e:
            logger.error(f"Failed to load resumes: {str(e)}")
            return pd.DataFrame()

    def load_job_descriptions_csv(
        self, filename: str = "job_descriptions.csv", sample_size: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Load job descriptions from CSV file.

        Args:
            filename: Name of the CSV file
            sample_size: Optional number of samples to load

        Returns:
            pd.DataFrame: Job descriptions dataframe
        """
        file_path = self.raw_data_path / filename

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return pd.DataFrame()

        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} job descriptions from {filename}")

            if sample_size:
                df = df.sample(n=min(sample_size, len(df)), random_state=42)
                logger.info(f"Sampled {len(df)} job descriptions")

            return df

        except Exception as e:
            logger.error(f"Failed to load job descriptions: {str(e)}")
            return pd.DataFrame()

    def create_train_test_split(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        random_state: int = 42,
        output_prefix: str = "data",
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data into train and test sets.

        Args:
            df: Input dataframe
            test_size: Proportion of test set (default 0.2 for 80/20 split)
            random_state: Random seed for reproducibility
            output_prefix: Prefix for output files

        Returns:
            Tuple of (train_df, test_df)
        """
        from sklearn.model_selection import train_test_split

        train_df, test_df = train_test_split(
            df, test_size=test_size, random_state=random_state
        )

        logger.info(
            f"Data split: {len(train_df)} train, {len(test_df)} test "
            f"({test_size*100}% test)"
        )

        # Save split data
        train_path = self.processed_data_path / f"{output_prefix}_train.csv"
        test_path = self.processed_data_path / f"{output_prefix}_test.csv"

        train_df.to_csv(train_path, index=False)
        test_df.to_csv(test_path, index=False)

        logger.info(f"Train set saved to {train_path}")
        logger.info(f"Test set saved to {test_path}")

        return train_df, test_df

    def load_json_dataset(self, filename: str) -> List[dict]:
        """
        Load JSON dataset.

        Args:
            filename: Name of the JSON file

        Returns:
            List of dictionaries
        """
        file_path = self.raw_data_path / filename

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} records from {filename}")
            return data

        except Exception as e:
            logger.error(f"Failed to load JSON dataset: {str(e)}")
            return []

    def get_dataset_info(self) -> dict:
        """
        Get information about available datasets in raw data directory.

        Returns:
            dict: Information about available datasets
        """
        info = {"csv_files": [], "json_files": [], "total_files": 0}

        try:
            for file in self.raw_data_path.iterdir():
                if file.suffix == ".csv":
                    info["csv_files"].append(
                        {"name": file.name, "size_mb": file.stat().st_size / (1024 * 1024)}
                    )
                elif file.suffix == ".json":
                    info["json_files"].append(
                        {"name": file.name, "size_mb": file.stat().st_size / (1024 * 1024)}
                    )

            info["total_files"] = len(info["csv_files"]) + len(info["json_files"])
            logger.info(f"Found {info['total_files']} dataset files")

        except Exception as e:
            logger.error(f"Failed to get dataset info: {str(e)}")

        return info


def load_sample_datasets() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load or create sample datasets for testing.

    Returns:
        Tuple of (sample_resumes, sample_jds)
    """
    loader = KaggleDataLoader()

    # Try to load from CSV files
    resumes_df = loader.load_resumes_csv()
    jds_df = loader.load_job_descriptions_csv()

    # If files don't exist, create sample data
    if resumes_df.empty:
        logger.info("Creating sample resume data...")
        resumes_df = pd.DataFrame(
            {
                "id": [f"resume_{i}" for i in range(50)],
                "name": [
                    "John Doe",
                    "Jane Smith",
                    "Mike Johnson",
                    "Sarah Williams",
                    "Tom Brown",
                ] * 10,
                "text": [
                    """JOHN DOE
                    Email: john@example.com | Phone: (555) 123-4567
                    
                    PROFESSIONAL SUMMARY
                    Experienced Software Engineer with 5+ years in Python development.
                    
                    EXPERIENCE
                    Senior Python Developer - Tech Company (2021-Present)
                    - Developed Python applications using FastAPI
                    - Implemented machine learning models
                    
                    SKILLS
                    Python, FastAPI, Machine Learning, Docker, Git"""
                ]
                * 50,
            }
        )

    if jds_df.empty:
        logger.info("Creating sample job description data...")
        jds_df = pd.DataFrame(
            {
                "id": [f"jd_{i}" for i in range(10)],
                "title": [
                    "Senior Python Developer",
                    "Junior Developer",
                    "Machine Learning Engineer",
                    "Full Stack Developer",
                    "DevOps Engineer",
                ] * 2,
                "text": [
                    """Senior Python Developer
                    
                    We are looking for a Senior Python Developer with:
                    - 5+ years of Python development
                    - FastAPI and REST API experience
                    - Machine Learning background
                    - Docker and containerization
                    
                    Requirements:
                    - Strong Python skills
                    - Experience with scikit-learn
                    - Git version control"""
                ]
                * 10,
            }
        )

    return resumes_df, jds_df


if __name__ == "__main__":
    # Example usage
    loader = KaggleDataLoader()

    # Check dataset info
    info = loader.get_dataset_info()
    print("Available datasets:", info)

    # Load sample data
    resumes, jds = load_sample_datasets()
    print(f"\nLoaded {len(resumes)} resumes and {len(jds)} job descriptions")

    # Create train/test split
    if not resumes.empty:
        train, test = loader.create_train_test_split(resumes, test_size=0.2)
        print(f"Train/test split completed: {len(train)} train, {len(test)} test")
