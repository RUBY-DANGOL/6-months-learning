"""Create intentionally drifted production data and an Evidently HTML report."""

from __future__ import annotations

import json

import mlflow
import numpy as np
import pandas as pd
from evidently import Report
from evidently.metrics import DriftedColumnsCount, ValueDrift
from sklearn.model_selection import train_test_split

from .config import ARTIFACT_DIR, EXPERIMENT, RANDOM_STATE, TRACKING_URI, ensure_directories
from .data import load_data


def build_slices() -> tuple[pd.DataFrame, pd.DataFrame]:
    X, y = load_data()
    full = X.copy(); full["Churn"] = y
    reference, current = train_test_split(
        full, test_size=0.30, stratify=full["Churn"], random_state=RANDOM_STATE
    )
    current = current.copy()
    rng = np.random.default_rng(RANDOM_STATE)
    current["MonthlyCharges"] = (current["MonthlyCharges"] +
                                 rng.normal(loc=22.0, scale=5.0, size=len(current))).clip(0)
    # Make Month-to-month dominate without changing row count.
    change = rng.random(len(current)) < 0.55
    current.loc[change, "Contract"] = "Month-to-month"
    # Explicit concept/target drift for the target drift check.
    flip = rng.random(len(current)) < 0.08
    current.loc[flip, "Churn"] = 1 - current.loc[flip, "Churn"]
    return reference.reset_index(drop=True), current.reset_index(drop=True)


def run_monitoring() -> dict:
    ensure_directories()
    reference, current = build_slices()
    report = Report(metrics=[DriftedColumnsCount(), ValueDrift(column="MonthlyCharges"),
                             ValueDrift(column="Contract"), ValueDrift(column="Churn")])
    snapshot = report.run(reference_data=reference, current_data=current)
    html_path = ARTIFACT_DIR / "data_drift_report.html"
    json_path = ARTIFACT_DIR / "data_drift_report.json"
    snapshot.save_html(str(html_path))
    snapshot.save_json(str(json_path))
    custom = {
        "metric": "mean_monthly_charges_shift",
        "reference_mean": float(reference["MonthlyCharges"].mean()),
        "current_mean": float(current["MonthlyCharges"].mean()),
        "absolute_difference": float(current["MonthlyCharges"].mean() -
                                     reference["MonthlyCharges"].mean()),
        "reference_churn_rate": float(reference["Churn"].mean()),
        "current_churn_rate": float(current["Churn"].mean()),
    }
    custom["action"] = ("recommend_retraining" if custom["absolute_difference"] > 10
                        else "continue_monitoring")
    custom_path = ARTIFACT_DIR / "custom_metrics.json"
    custom_path.write_text(json.dumps(custom, indent=2), encoding="utf-8")
    mlflow.set_tracking_uri(TRACKING_URI); mlflow.set_experiment(EXPERIMENT)
    with mlflow.start_run(run_name="production-drift-check"):
        mlflow.log_metrics({k: v for k, v in custom.items() if isinstance(v, float)})
        mlflow.log_artifact(str(html_path), artifact_path="monitoring")
        mlflow.log_artifact(str(json_path), artifact_path="monitoring")
        mlflow.log_artifact(str(custom_path), artifact_path="monitoring")
    return custom


if __name__ == "__main__":
    print(json.dumps(run_monitoring(), indent=2))

