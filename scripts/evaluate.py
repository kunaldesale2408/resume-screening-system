"""
Measure how well the screener agrees with human labels.

Input: a CSV with one row per (resume, job) pair and a human label:

    resume,job,label
    alice.pdf,ml_engineer.txt,1
    bob.pdf,ml_engineer.txt,0

    resume / job : file paths, relative to the CSV's folder (PDF, DOCX or TXT)
    label        : 1 = the recruiter would shortlist this resume for this job, 0 = not

All resumes for the same job are scored together as one batch, exactly as
in the app. The script reports:

  - accuracy, precision, recall and F1 at the configured shortlist threshold
  - ROC-AUC (how well the score ranks fit above not-fit, threshold-free)
  - precision@k for each job (of the top k ranked resumes, how many are fit)
  - the threshold that maximises F1 on this data (choosing a threshold on
    the same data you report on is optimistic; confirm it on a separate set)
  - average processing time per resume

Usage:
    python scripts/evaluate.py path/to/labels.csv [--k 5] [--out report.json]
    python scripts/evaluate.py tests/fixtures/eval_demo/labels.csv   # synthetic demo
"""

import argparse
import csv
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sklearn.metrics import (  # noqa: E402
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from src.api.services import get_scorer, score_texts  # noqa: E402
from src.preprocessing import extract_text  # noqa: E402


def load_labels(csv_path: Path):
    with open(csv_path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    missing = {"resume", "job", "label"} - set(rows[0].keys() if rows else [])
    if missing:
        raise SystemExit(f"{csv_path} is missing column(s): {', '.join(sorted(missing))}")
    for row in rows:
        row["label"] = int(row["label"])
        if row["label"] not in (0, 1):
            raise SystemExit(f"Labels must be 0 or 1, got {row['label']} for {row['resume']}")
    return rows


def read_file(path: Path) -> str:
    return extract_text(path.read_bytes(), path.name)


def evaluate(csv_path: Path, k: int = 5) -> dict:
    base = csv_path.parent
    rows = load_labels(csv_path)

    by_job = defaultdict(list)
    for row in rows:
        by_job[row["job"]].append(row)

    y_true, y_score, per_job = [], [], {}
    n_resumes, total_seconds = 0, 0.0

    for job_file, job_rows in by_job.items():
        job_text = read_file(base / job_file)
        resumes = [(r["resume"], read_file(base / r["resume"])) for r in job_rows]
        start = time.perf_counter()
        response = score_texts(job_text, resumes)
        total_seconds += time.perf_counter() - start
        n_resumes += len(resumes)

        scores = {r["filename"]: r["overall_score"] for r in response["results"]}
        labels = {r["resume"]: r["label"] for r in job_rows}
        for name, label in labels.items():
            y_true.append(label)
            y_score.append(scores[name])

        ranked = [r["filename"] for r in response["results"]]
        # If a job has fewer fit resumes than k, precision@k can't reach 1.0,
        # so k is capped at the number of fit resumes (R-precision).
        k_job = min(k, len(ranked), max(sum(labels.values()), 1))
        top = ranked[:k_job]
        per_job[job_file] = {
            "resumes": len(ranked),
            "fit_resumes": sum(labels.values()),
            f"precision_at_{len(top)}": round(sum(labels[n] for n in top) / len(top), 3),
            "ranking": [{"resume": n, "score": scores[n], "label": labels[n]} for n in ranked],
        }

    threshold = get_scorer().thresholds["similarity_threshold"]
    report = {
        "pairs": len(y_true),
        "positives": sum(y_true),
        "threshold": threshold,
        "at_threshold": _metrics(y_true, y_score, threshold),
        "roc_auc": round(roc_auc_score(y_true, y_score), 3) if len(set(y_true)) == 2 else None,
        "best_f1_threshold": _best_threshold(y_true, y_score),
        "per_job": per_job,
        "seconds_per_resume": round(total_seconds / max(n_resumes, 1), 3),
    }
    return report


def _metrics(y_true, y_score, threshold):
    y_pred = [int(s >= threshold) for s in y_score]
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 3),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 3),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 3),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 3),
    }


def _best_threshold(y_true, y_score):
    best = None
    for t in sorted(set(y_score)):
        m = _metrics(y_true, y_score, t)
        if best is None or m["f1"] > best["metrics"]["f1"]:
            best = {"threshold": round(t, 4), "metrics": m}
    return best


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("labels_csv", type=Path)
    parser.add_argument("--k", type=int, default=5, help="k for precision@k (default 5)")
    parser.add_argument("--out", type=Path, help="also write the full report as JSON")
    args = parser.parse_args(argv)

    report = evaluate(args.labels_csv, k=args.k)

    m = report["at_threshold"]
    print(f"Pairs evaluated : {report['pairs']} ({report['positives']} labelled fit)")
    print(f"Threshold       : {report['threshold']}")
    print(f"Accuracy        : {m['accuracy']:.3f}")
    print(f"Precision       : {m['precision']:.3f}")
    print(f"Recall          : {m['recall']:.3f}")
    print(f"F1              : {m['f1']:.3f}")
    print(f"ROC-AUC         : {report['roc_auc']}")
    best = report["best_f1_threshold"]
    print(f"Best-F1 threshold on this data: {best['threshold']} (F1 {best['metrics']['f1']:.3f}; optimistic)")
    print(f"Seconds/resume  : {report['seconds_per_resume']}")
    for job, info in report["per_job"].items():
        p_key = next(key for key in info if key.startswith("precision_at_"))
        print(f"  {job}: {info[p_key]:.2f} {p_key.replace('_', ' ')}, {info['fit_resumes']}/{info['resumes']} fit")

    if args.out:
        args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Full report written to {args.out}")
    return report


if __name__ == "__main__":
    main()
