"""
Validation module for Resume Screening System.

Validates system accuracy on manually labeled datasets.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

logger = logging.getLogger(__name__)


class Validator:
    """
    Validates resume matching accuracy on labeled datasets.
    """

    def __init__(self, threshold: float = 0.5):
        """
        Initialize validator.

        Args:
            threshold: Score threshold for positive prediction (0-1)
        """
        self.threshold = threshold
        self.results = {}

    def validate_on_labeled_set(
        self,
        predictions: List[float],
        ground_truth: List[int],
    ) -> Dict:
        """
        Validate predictions against ground truth.

        Args:
            predictions: List of predicted scores (0-1)
            ground_truth: List of ground truth labels (0 or 1)

        Returns:
            dict: Validation metrics
        """
        # Convert scores to binary predictions
        binary_predictions = [1 if p >= self.threshold else 0 for p in predictions]

        # Calculate metrics
        accuracy = accuracy_score(ground_truth, binary_predictions)
        precision = precision_score(ground_truth, binary_predictions, zero_division=0)
        recall = recall_score(ground_truth, binary_predictions, zero_division=0)
        f1 = f1_score(ground_truth, binary_predictions, zero_division=0)

        # Additional metrics
        tp = sum([1 for p, g in zip(binary_predictions, ground_truth) if p == 1 and g == 1])
        tn = sum([1 for p, g in zip(binary_predictions, ground_truth) if p == 0 and g == 0])
        fp = sum([1 for p, g in zip(binary_predictions, ground_truth) if p == 1 and g == 0])
        fn = sum([1 for p, g in zip(binary_predictions, ground_truth) if p == 0 and g == 1])

        return {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "true_positives": tp,
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "threshold": self.threshold,
        }

    def validate_multiple_thresholds(
        self,
        predictions: List[float],
        ground_truth: List[int],
        thresholds: List[float] = None,
    ) -> Dict:
        """
        Validate predictions at multiple thresholds.

        Args:
            predictions: List of predicted scores
            ground_truth: List of ground truth labels
            thresholds: List of thresholds to test

        Returns:
            dict: Metrics for each threshold
        """
        if thresholds is None:
            thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

        results = {}

        for threshold in thresholds:
            self.threshold = threshold
            metrics = self.validate_on_labeled_set(predictions, ground_truth)
            results[threshold] = metrics

        return results

    def calculate_confusion_matrix(
        self,
        predictions: List[float],
        ground_truth: List[int],
    ) -> np.ndarray:
        """
        Calculate confusion matrix.

        Args:
            predictions: List of predicted scores
            ground_truth: List of ground truth labels

        Returns:
            np.ndarray: 2x2 confusion matrix
        """
        binary_predictions = [1 if p >= self.threshold else 0 for p in predictions]

        tp = sum([1 for p, g in zip(binary_predictions, ground_truth) if p == 1 and g == 1])
        tn = sum([1 for p, g in zip(binary_predictions, ground_truth) if p == 0 and g == 0])
        fp = sum([1 for p, g in zip(binary_predictions, ground_truth) if p == 1 and g == 0])
        fn = sum([1 for p, g in zip(binary_predictions, ground_truth) if p == 0 and g == 1])

        return np.array([[tn, fp], [fn, tp]])

    def calculate_roc_metrics(
        self,
        predictions: List[float],
        ground_truth: List[int],
    ) -> Dict:
        """
        Calculate ROC curve metrics.

        Args:
            predictions: List of predicted scores
            ground_truth: List of ground truth labels

        Returns:
            dict: ROC metrics
        """
        try:
            from sklearn.metrics import auc, roc_curve

            fpr, tpr, thresholds = roc_curve(ground_truth, predictions)
            roc_auc = auc(fpr, tpr)

            return {
                "roc_auc": round(roc_auc, 4),
                "fpr": fpr.tolist(),
                "tpr": tpr.tolist(),
                "thresholds": thresholds.tolist(),
            }
        except Exception as e:
            logger.error(f"ROC calculation failed: {str(e)}")
            return {}

    def generate_report(
        self,
        predictions: List[float],
        ground_truth: List[int],
        output_file: str = None,
    ) -> Dict:
        """
        Generate comprehensive validation report.

        Args:
            predictions: List of predicted scores
            ground_truth: List of ground truth labels
            output_file: Optional file to save report

        Returns:
            dict: Complete validation report
        """
        logger.info(f"Generating validation report ({len(predictions)} samples)...")

        report = {
            "summary": self.validate_on_labeled_set(predictions, ground_truth),
            "threshold_analysis": self.validate_multiple_thresholds(
                predictions, ground_truth
            ),
            "confusion_matrix": self.calculate_confusion_matrix(
                predictions, ground_truth
            ).tolist(),
            "roc_metrics": self.calculate_roc_metrics(predictions, ground_truth),
            "dataset_size": len(predictions),
            "positive_samples": sum(ground_truth),
            "negative_samples": len(ground_truth) - sum(ground_truth),
        }

        if output_file:
            try:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, "w") as f:
                    json.dump(report, f, indent=2)

                logger.info(f"Report saved to {output_path}")
            except Exception as e:
                logger.error(f"Failed to save report: {str(e)}")

        return report


if __name__ == "__main__":
    # Example usage
    predictions = [0.9, 0.8, 0.3, 0.2, 0.7, 0.6, 0.4, 0.85, 0.15, 0.95]
    ground_truth = [1, 1, 0, 0, 1, 1, 0, 1, 0, 1]

    validator = Validator(threshold=0.5)

    # Single threshold validation
    metrics = validator.validate_on_labeled_set(predictions, ground_truth)
    print("Validation Metrics:")
    print(json.dumps(metrics, indent=2))

    # Generate report
    report = validator.generate_report(
        predictions, ground_truth, "validation_report.json"
    )
    print("\nReport generated successfully")
