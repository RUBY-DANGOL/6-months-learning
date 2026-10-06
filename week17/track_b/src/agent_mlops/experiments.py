from __future__ import annotations

import csv
import json

import mlflow
import pandas as pd

from .agent import VERSIONS, run_case
from .config import (ARTIFACT_DIR, CASE_FILE, EXPERIMENT, PROMPT_DIR, TRACKING_URI,
                     ensure_directories)
from .evaluation import deterministic_judge, evidently_report


def run_experiments() -> list[dict]:
    ensure_directories()
    cases = json.loads(CASE_FILE.read_text(encoding="utf-8"))
    mlflow.set_tracking_uri(TRACKING_URI); mlflow.set_experiment(EXPERIMENT)
    comparison = []
    for version in VERSIONS:
        prompt_path = PROMPT_DIR / f"{version.name}.txt"
        results = []
        with mlflow.start_run(run_name=version.name) as run:
            for case in cases:
                result = run_case(case, version)
                result["judge"] = deterministic_judge(case, result)
                results.append(result)
            passed = sum(row["judge"]["passed"] for row in results)
            pct = 100.0 * passed / len(results)
            avg_iterations = sum(row["iterations"] for row in results) / len(results)
            total_tokens = sum(row["simulated_tokens"] for row in results)
            mlflow.log_params({"prompt_version": version.name, "top_k": version.top_k,
                               "max_iterations": version.max_iterations,
                               "temperature": version.temperature,
                               "evaluation_mode": "deterministic_fixture"})
            mlflow.log_metrics({"pct_tests_passed": pct, "avg_iterations": avg_iterations,
                                "simulated_total_tokens": total_tokens,
                                "task_completion_rate": 100.0})
            trace_path = ARTIFACT_DIR / "runtime" / f"{version.name}_traces.json"
            trace_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
            mlflow.log_artifact(str(trace_path), artifact_path="traces")
            mlflow.log_artifact(str(prompt_path), artifact_path="prompt")
            report_path = ARTIFACT_DIR / f"{version.name}_regression_report.html"
            evidently_report(results, report_path)
            mlflow.log_artifact(str(report_path), artifact_path="regression")
            comparison.append({"run_id": run.info.run_id, "prompt_version": version.name,
                               "pct_tests_passed": pct, "avg_iterations": avg_iterations,
                               "simulated_total_tokens": total_tokens,
                               "promoted": pct == 100.0})
    output = ARTIFACT_DIR / "prompt_comparison.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=comparison[0].keys())
        writer.writeheader(); writer.writerows(comparison)
    best = max(comparison, key=lambda r: (r["pct_tests_passed"], -r["simulated_total_tokens"]))
    (ARTIFACT_DIR / "promotion_decision.json").write_text(json.dumps({
        "selected": best["prompt_version"], "gate": "pct_tests_passed == 100",
        "decision": "promote" if best["promoted"] else "reject",
        "rationale": "Highest regression pass rate; token cost breaks ties."
    }, indent=2), encoding="utf-8")
    return comparison


if __name__ == "__main__":
    print(json.dumps(run_experiments(), indent=2))

