"""The evaluation script runs end to end on the synthetic demo set."""

from pathlib import Path

from scripts.evaluate import evaluate

DEMO = Path(__file__).parent / "fixtures" / "eval_demo" / "labels.csv"


def test_evaluate_demo_set():
    report = evaluate(DEMO, k=5)
    assert report["pairs"] == 12
    assert set(report["at_threshold"]) == {"accuracy", "precision", "recall", "f1"}
    # On this easy synthetic set, every labelled-fit resume should rank at the top for its job.
    for info in report["per_job"].values():
        n_fit = info["fit_resumes"]
        assert all(row["label"] == 1 for row in info["ranking"][:n_fit])
