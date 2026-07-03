"""
Data processing pipeline orchestration for Resume Screening System.

Orchestrates the full preprocessing workflow from raw data to cleaned features.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from src.config import settings
from src.data_loader import KaggleDataLoader, load_sample_datasets
from src.preprocessing.pdf_extractor import PDFExtractor
from src.preprocessing.text_cleaner import TextCleaner

logger = logging.getLogger(__name__)


class DataPipeline:
    """
    Orchestrates the complete data preprocessing pipeline.
    """

    def __init__(
        self,
        use_ocr: bool = True,
        remove_stopwords: bool = True,
        save_intermediate: bool = False,
    ):
        """
        Initialize the data pipeline.

        Args:
            use_ocr: Whether to use OCR for PDF extraction
            remove_stopwords: Whether to remove stopwords during cleaning
            save_intermediate: Whether to save intermediate results
        """
        self.data_loader = KaggleDataLoader()
        self.pdf_extractor = PDFExtractor(use_ocr=use_ocr)
        self.text_cleaner = TextCleaner(remove_stopwords=remove_stopwords)
        self.save_intermediate = save_intermediate
        self.processed_data_path = settings.PROCESSED_DATA_PATH
        self.stats = {}

    def process_resumes_dataframe(
        self, df: pd.DataFrame, text_column: str = "text", output_file: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Process a dataframe of resumes.

        Args:
            df: Dataframe with resume text
            text_column: Name of the column containing resume text
            output_file: Optional output CSV file name

        Returns:
            pd.DataFrame: Processed dataframe with cleaned text and tokens
        """
        logger.info(f"Processing {len(df)} resumes...")
        processed_df = df.copy()

        # Clean text
        logger.debug("Cleaning resume text...")
        processed_df["text_cleaned"] = processed_df[text_column].apply(
            lambda x: self.text_cleaner.clean(x) if isinstance(x, str) else ""
        )

        # Tokenize
        logger.debug("Tokenizing text...")
        processed_df["tokens"] = processed_df["text_cleaned"].apply(
            lambda x: self.text_cleaner.process_full_pipeline(x)
        )

        # Calculate text statistics
        logger.debug("Calculating text statistics...")
        processed_df["word_count"] = processed_df["tokens"].apply(len)
        processed_df["char_count"] = processed_df["text_cleaned"].apply(len)

        # Save if requested
        if output_file:
            output_path = self.processed_data_path / output_file
            processed_df.to_csv(output_path, index=False)
            logger.info(f"Processed resumes saved to {output_path}")

        logger.info(f"Resume processing complete. Avg words: {processed_df['word_count'].mean():.0f}")
        self.stats["resumes_processed"] = len(df)
        self.stats["avg_resume_words"] = processed_df["word_count"].mean()

        return processed_df

    def process_job_descriptions_dataframe(
        self, df: pd.DataFrame, text_column: str = "text", output_file: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Process a dataframe of job descriptions.

        Args:
            df: Dataframe with job description text
            text_column: Name of the column containing JD text
            output_file: Optional output CSV file name

        Returns:
            pd.DataFrame: Processed dataframe with cleaned text and tokens
        """
        logger.info(f"Processing {len(df)} job descriptions...")
        processed_df = df.copy()

        # Clean text
        logger.debug("Cleaning JD text...")
        processed_df["text_cleaned"] = processed_df[text_column].apply(
            lambda x: self.text_cleaner.clean(x) if isinstance(x, str) else ""
        )

        # Tokenize
        logger.debug("Tokenizing text...")
        processed_df["tokens"] = processed_df["text_cleaned"].apply(
            lambda x: self.text_cleaner.process_full_pipeline(x)
        )

        # Calculate text statistics
        logger.debug("Calculating text statistics...")
        processed_df["word_count"] = processed_df["tokens"].apply(len)
        processed_df["char_count"] = processed_df["text_cleaned"].apply(len)

        # Save if requested
        if output_file:
            output_path = self.processed_data_path / output_file
            processed_df.to_csv(output_path, index=False)
            logger.info(f"Processed JDs saved to {output_path}")

        logger.info(f"JD processing complete. Avg words: {processed_df['word_count'].mean():.0f}")
        self.stats["jds_processed"] = len(df)
        self.stats["avg_jd_words"] = processed_df["word_count"].mean()

        return processed_df

    def process_pdf_files(self, pdf_directory: Path) -> Dict[str, str]:
        """
        Process all PDF files in a directory.

        Args:
            pdf_directory: Path to directory containing PDF files

        Returns:
            Dict mapping filename to extracted and cleaned text
        """
        pdf_directory = Path(pdf_directory)

        if not pdf_directory.exists():
            logger.error(f"Directory not found: {pdf_directory}")
            return {}

        pdf_files = list(pdf_directory.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")

        results = {}

        for idx, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"Processing {idx}/{len(pdf_files)}: {pdf_file.name}")

            # Extract text
            text = self.pdf_extractor.extract_text(str(pdf_file))

            # Clean text
            cleaned_text = self.text_cleaner.clean(text)

            results[pdf_file.name] = cleaned_text

        logger.info(f"PDF processing complete: {len(results)} files processed")
        self.stats["pdfs_processed"] = len(results)

        return results

    def run_full_pipeline(
        self,
        resumes_df: Optional[pd.DataFrame] = None,
        jds_df: Optional[pd.DataFrame] = None,
        use_sample_data: bool = False,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Run the complete preprocessing pipeline.

        Args:
            resumes_df: Resumes dataframe (if None, loads from file)
            jds_df: Job descriptions dataframe (if None, loads from file)
            use_sample_data: Whether to create sample data if files don't exist

        Returns:
            Tuple of (processed_resumes, processed_jds)
        """
        logger.info("Starting full data pipeline...")

        # Load data if not provided
        if resumes_df is None or jds_df is None:
            if use_sample_data:
                logger.info("Loading sample datasets...")
                resumes_df, jds_df = load_sample_datasets()
            else:
                logger.info("Loading datasets from files...")
                resumes_df = self.data_loader.load_resumes_csv()
                jds_df = self.data_loader.load_job_descriptions_csv()

        # Process dataframes
        processed_resumes = self.process_resumes_dataframe(
            resumes_df, output_file="resumes_processed.csv"
        )
        processed_jds = self.process_job_descriptions_dataframe(
            jds_df, output_file="jds_processed.csv"
        )

        # Save pipeline statistics
        self._save_statistics()

        logger.info("Full pipeline completed successfully")

        return processed_resumes, processed_jds

    def _save_statistics(self) -> None:
        """
        Save pipeline statistics to JSON file.
        """
        stats_file = self.processed_data_path / "pipeline_stats.json"

        try:
            with open(stats_file, "w") as f:
                json.dump(self.stats, f, indent=2)
            logger.info(f"Statistics saved to {stats_file}")
        except Exception as e:
            logger.error(f"Failed to save statistics: {str(e)}")

    def get_statistics(self) -> Dict:
        """
        Get pipeline execution statistics.

        Returns:
            dict: Processing statistics
        """
        return self.stats.copy()


def preprocess_documents(
    resumes_text_list: List[str], jds_text_list: List[str]
) -> Tuple[List[str], List[str]]:
    """
    Convenience function to preprocess lists of documents.

    Args:
        resumes_text_list: List of resume texts
        jds_text_list: List of job description texts

    Returns:
        Tuple of (cleaned_resumes, cleaned_jds)
    """
    pipeline = DataPipeline()

    cleaned_resumes = [
        pipeline.text_cleaner.clean(text) if isinstance(text, str) else "" 
        for text in resumes_text_list
    ]
    cleaned_jds = [
        pipeline.text_cleaner.clean(text) if isinstance(text, str) else "" 
        for text in jds_text_list
    ]

    return cleaned_resumes, cleaned_jds


if __name__ == "__main__":
    # Example usage
    pipeline = DataPipeline(use_ocr=False, remove_stopwords=True)

    # Run with sample data
    processed_resumes, processed_jds = pipeline.run_full_pipeline(use_sample_data=True)

    print(f"\nProcessed {len(processed_resumes)} resumes")
    print(f"Processed {len(processed_jds)} job descriptions")
    print(f"\nStatistics: {pipeline.get_statistics()}")
