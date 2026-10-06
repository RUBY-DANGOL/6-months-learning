"""Train candidates, log complete evidence, and promote the best model."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow import MlflowClient
from mlflow.models import infer_signature
from sklearn.metrics import (ConfusionMatrixDisplay, RocCurveDisplay, accuracy_score,
                             f1_score, precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split

from .config import (ARTIFACT_DIR, EXPERIMENT, MODEL_NAME, RANDOM_STATE, TRACKING_URI,
                     ensure_directories)
from .data import load_data
from .modeling import CANDIDATES, make_pipeline


def classification_metrics(y_true, prediction, probability) -> dict[str, float]:
    return {
        "accuracy": accuracy_score(y_true, prediction),
        "precision": precision_score(y_true, prediction, zero_division=0),
        "recall": recall_score(y_true, prediction, zero_division=0),
        "f1": f1_score(y_true, prediction, zero_division=0),
        "roc_auc": roc_auc_score(y_true, probability),
    }


def _plots(y_true, prediction, probability, output: Path) -> tuple[Path, Path]:
    output.mkdir(parents=True, exist_ok=True)
    confusion = output / "confusion_matrix.png"
    roc = output / "roc_curve.png"
    ConfusionMatrixDisplay.from_predictions(y_true, prediction, display_labels=["No", "Yes"])
    plt.tight_layout(); plt.savefig(confusion, dpi=140); plt.close()
    RocCurveDisplay.from_predictions(y_true, probability)
    plt.tight_layout(); plt.savefig(roc, dpi=140); plt.close()
    return confusion, roc


def run_training() -> dict:
    ensure_directories()
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=RANDOM_STATE
    )
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT)
    rows = []
    for candidate in CANDIDATES:
        with mlflow.start_run(run_name=candidate.name) as run:
            model = make_pipeline(X_train, candidate)
            model.fit(X_train, y_train)
            prediction = model.predict(X_test)
            probability = model.predict_proba(X_test)[:, 1]
            metrics = classification_metrics(y_test, prediction, probability)
            params = {"model_family": candidate.family, **candidate.params,
                      "class_weight": "balanced", "split_seed": RANDOM_STATE}
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            output = ARTIFACT_DIR / "runtime" / candidate.name
            confusion, roc = _plots(y_test, prediction, probability, output)
            mlflow.log_artifacts(str(output), artifact_path="evaluation")
            signature = infer_signature(X_train.head(20), model.predict(X_train.head(20)))
            mlflow.sklearn.log_model(model, name="model", signature=signature,
                                     input_example=X_train.head(3))
            rows.append({"run_id": run.info.run_id, "run_name": candidate.name,
                         **params, **metrics})

    rows.sort(key=lambda row: (row["f1"], row["roc_auc"]), reverse=True)
    comparison = ARTIFACT_DIR / "model_comparison.csv"
    fieldnames = list(dict.fromkeys(key for row in rows for key in row))
    with comparison.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader(); writer.writerows(rows)
    best = rows[0]
    result = mlflow.register_model(f"runs:/{best['run_id']}/model", MODEL_NAME)
    client = MlflowClient()
    version = str(result.version)
    # Stages are deprecated in MLflow 3, so aliases and lifecycle tags represent both transitions.
    client.set_registered_model_alias(MODEL_NAME, "staging", version)
    client.set_model_version_tag(MODEL_NAME, version, "lifecycle", "staging")
    client.set_registered_model_alias(MODEL_NAME, "champion", version)
    client.set_model_version_tag(MODEL_NAME, version, "lifecycle", "production")
    registry = {"model_name": MODEL_NAME, "version": version, "run_id": best["run_id"],
                "transitions": ["staging", "production"],
                "aliases": ["staging", "champion"], "selection_metric": "f1",
                "selected_metrics": {k: best[k] for k in
                                     ("accuracy", "precision", "recall", "f1", "roc_auc")}}
    (ARTIFACT_DIR / "registry.json").write_text(json.dumps(registry, indent=2), encoding="utf-8")
    return registry


if __name__ == "__main__":
    print(json.dumps(run_training(), indent=2))
