# Track A — Telco Churn MLOps

## Screen recording

[Watch the Track A demonstration](<Screen Recording 2026-10-06 071224.mp4>)

This project trains and compares three churn classifiers, registers the strongest model, serves
its registry alias with FastAPI, and detects deliberately injected production drift. The compact
comparison and monitoring evidence in `artifacts/` was produced by the checked-in pipeline.

## Environment and reproducibility

The earlier notebook-style work did not lock transitive versions, which made MLflow, Evidently,
scikit-learn, and SQLAlchemy especially vulnerable to incompatible upgrades. `pyproject.toml`
declares the direct dependencies and `uv.lock` pins the complete Python 3.11 environment.

From a clean clone:

```powershell
uv sync --frozen
uv run python scripts/run_all.py
uv run pytest
```

The first pipeline run downloads the public IBM Telco Customer Churn CSV into `data/`. A cached
copy is then reused. `OPENBLAS_NUM_THREADS=1` may be set on a memory-constrained machine.

## Experiment tracking strategy

All candidates use the same stratified 75/25 split, balanced class weights, preprocessing, and
seed. The genuinely varied configurations are two L2 logistic regressions (`C=0.25` and `C=1`)
and a 300-tree random forest (`max_depth=8`, `min_samples_leaf=3`). Every MLflow run records its
parameters, accuracy, precision, recall, F1, ROC-AUC, model, signature, input example, confusion
matrix, and ROC curve.

| Run | Accuracy | Precision | Recall | F1 | ROC-AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| random forest, 300 trees/depth 8 | **0.7649** | **0.5391** | 0.7816 | **0.6381** | 0.8448 |
| logistic regression, C=0.25 | 0.7518 | 0.5210 | **0.7966** | 0.6300 | 0.8459 |
| logistic regression, C=1.0 | 0.7496 | 0.5182 | 0.7944 | 0.6272 | **0.8460** |

The random forest was registered because F1 is the primary selection metric for this imbalanced
target and it achieved the highest F1 (0.6381), as well as the best accuracy and precision. The
logistic models had marginally better recall/ROC-AUC, so the decision is an explicit trade-off:
better balanced classification rather than optimizing ranking alone. The full exported table is
[`artifacts/model_comparison.csv`](artifacts/model_comparison.csv).

The winner is registered as `TelcoChurnClassifier`. MLflow 3 deprecates fixed registry stages, so
the pipeline records both lifecycle transitions (`staging` then `production`) as model-version
tags and uses the supported `staging` and `champion` aliases. See
[`artifacts/registry.json`](artifacts/registry.json).

Inspect runs and registry:

```powershell
uv run mlflow ui --backend-store-uri sqlite:///artifacts/runtime/mlflow.db --port 5000 --workers 1
```

## Serving

The API loads `models:/TelcoChurnClassifier@champion`, not a hard-coded file:

```powershell
uv run uvicorn churn_mlops.api:app --port 8000
```

`GET /health` identifies the served alias. `POST /predict` accepts `{"records": [{...all raw
Telco feature fields...}]}`. The logged preprocessing pipeline handles numeric scaling and
categorical one-hot encoding before prediction.

## Monitoring and drift strategy

The reference population is the stratified 70% training-time slice. Current is the held-out 30%
production-like slice. The pipeline shifts `MonthlyCharges` by normally distributed noise with a
mean of 22, changes roughly 55% of current contracts to `Month-to-month`, and flips 8% of labels.
Evidently measures overall drift and individual drift for `MonthlyCharges`, `Contract`, and
`Churn` (target drift).

The project-specific metric is the mean MonthlyCharges difference. It measured **+21.10**
(`64.95 → 86.05`); the churn rate also changed from **26.53% to 30.95%**. This confirms that the
engineered feature and target shifts were detected. A charge shift this large can alter the
relationship learned by the classifier and the changed contract mix can move the decision
boundary's operating population. The action rule recommends retraining whenever the absolute
mean-charge shift exceeds 10. The run therefore produced `recommend_retraining`.

Evidence:

- [`artifacts/data_drift_report.html`](artifacts/data_drift_report.html) — interactive Evidently report
- [`artifacts/data_drift_report.json`](artifacts/data_drift_report.json) — machine-readable metrics
- [`artifacts/custom_metrics.json`](artifacts/custom_metrics.json) — custom metric and action

The HTML, JSON, and custom metrics are also logged into the MLflow monitoring run.

## Workflow and layout

```text
IBM CSV → clean/split → train 3 pipelines → log/compare → register/alias champion
        → FastAPI serving → reference/current drift report → retraining recommendation
```

- `src/churn_mlops/`: data, modeling, training, monitoring, and API modules
- `scripts/run_all.py`: reproducible end-to-end entry point
- `tests/`: data, candidate, and drift invariants
- `artifacts/`: submission-sized exported evidence
