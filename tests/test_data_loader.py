"""
Tests for data loader module.
"""

import pytest
import pandas as pd
from pathlib import Path

from src.data_loader import KaggleDataLoader, load_sample_datasets


class TestKaggleDataLoader:
    """Tests for KaggleDataLoader class."""

    def test_initialization(self):
        """Test data loader initialization."""
        loader = KaggleDataLoader()
        assert loader.raw_data_path.exists()
        assert loader.processed_data_path.exists()

    def test_get_dataset_info(self):
        """Test getting dataset information."""
        loader = KaggleDataLoader()
        info = loader.get_dataset_info()
        assert isinstance(info, dict)
        assert "csv_files" in info
        assert "json_files" in info
        assert "total_files" in info

    def test_create_train_test_split(self):
        """Test creating train/test split."""
        loader = KaggleDataLoader()
        # Create sample dataframe
        df = pd.DataFrame({
            "id": range(100),
            "text": [f"Sample text {i}" for i in range(100)]
        })
        
        train, test = loader.create_train_test_split(df, test_size=0.2)
        assert len(train) == 80
        assert len(test) == 20
        assert len(train) + len(test) == len(df)


class TestLoadSampleDatasets:
    """Tests for load_sample_datasets function."""

    def test_load_sample_datasets(self):
        """Test loading sample datasets."""
        resumes, jds = load_sample_datasets()
        assert isinstance(resumes, pd.DataFrame)
        assert isinstance(jds, pd.DataFrame)
        assert len(resumes) > 0
        assert len(jds) > 0

    def test_sample_resumes_structure(self):
        """Test structure of sample resumes."""
        resumes, _ = load_sample_datasets()
        assert "id" in resumes.columns or "name" in resumes.columns
        assert "text" in resumes.columns

    def test_sample_jds_structure(self):
        """Test structure of sample JDs."""
        _, jds = load_sample_datasets()
        assert "id" in jds.columns or "title" in jds.columns
        assert "text" in jds.columns
