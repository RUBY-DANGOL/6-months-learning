# Week 17 — MLOps for predictive ML and an agentic assistant

This repository contains both required tracks. Each track has its own reproducible `uv`
environment, MLflow experiment, executable pipeline, generated evidence, tests, and detailed
README.

| Track | Project | What it demonstrates |
| --- | --- | --- |
| A | [`track_a`](track_a/) | Telco churn training, comparison, registry promotion, serving, and drift monitoring |
| B | [`track_b`](track_b/) | Versioned assistant prompts, full agent traces, regression gates, and prompt promotion |

## Reproduce everything

```powershell
cd track_a
uv sync --frozen
uv run python scripts/run_all.py
uv run pytest

cd ../track_b
uv sync --frozen
uv run python scripts/run_experiments.py
uv run pytest
```

The pipelines deliberately use local, deterministic inputs by default. This makes a clean-clone
run independent of paid APIs. Track B also documents an optional live LLM-judge path. Generated
evidence is written beneath each track's `artifacts/` directory; runtime-heavy MLflow stores are
ignored, while compact CSV/JSON/HTML evidence is committed.

## Standard workflow

```text
Track A: data → training → MLflow comparison → registry aliases → API → drift report → retrain gate
Track B: golden cases → prompt run → full traces → regression judge → MLflow comparison → promotion gate
```

Airflow was not implemented because it is optional. Both pipelines expose a single command that
can be placed in any scheduler; the action/threshold logic is part of the monitored run rather
than being represented by an untested DAG.

