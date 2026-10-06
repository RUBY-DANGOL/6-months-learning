# Track B — Agentic AI MLOps

## Screen recording

[Watch the Track B demonstration](<Screen Recording 2026-10-06 071716.mp4>)

This track applies reproducibility, experiment tracking, full tracing, and regression gates to
the Week 16 bounded policy-verification assistant. The local harness is deterministic so a clean
clone does not require a paid model. An optional path runs two native Evidently LLM judges with
an OpenAI key.

## Environment and reproducibility

Week 16 separated API/UI requirement files and did not lock the complete graph. Here,
`pyproject.toml` and `uv.lock` pin the shared MLflow/Evidently evaluation environment. Reproduce:

```powershell
uv sync --frozen
uv run python scripts/run_experiments.py
uv run pytest
```

The harness exercises the same W16 behavioral contract: a bounded loop chooses search, clarify,
or answer; citations must be supported; tool failure must not turn into invented policy.

## Prompt and trace experiment strategy

Three prompt files are explicit versioned artifacts. Each version responds to a traced failure:

1. `prompt_v1` says to stop when evidence seems sufficient. Its traces reveal early unsupported
   answers, missing citations, and a fabricated deadline after tool failure.
2. `prompt_v2` requires search, source citations, query refinement, and no invention. It fixes
   ordinary policy questions but its failure trace does not clearly disclose that search failed.
3. `prompt_v3` adds exact-quote grounding, rejection of unsupported answers, explicit tool-failure
   handling, and clear termination rules.

For every golden query, the trace JSON records each intermediate decision and reason, tool name,
arguments, raw return/error, iteration count, token estimate, and termination reason. All four
traces per version—success, ambiguity, regression, and failure—are logged as MLflow artifacts,
along with that version's prompt and Evidently report.

| Prompt | Regression pass | Avg. iterations | Simulated tokens | Promotion |
| --- | ---: | ---: | ---: | --- |
| v1 | 0% | 1.50 | 330 | rejected |
| v2 | 75% | 1.75 | 385 | rejected |
| v3 | **100%** | 1.75 | 385 | **promoted** |

Version 3 wins because it is the only version that passes every regression check. Its additional
55 simulated tokens versus v1 are justified by grounded search and failure handling; it costs no
more than v2. Token figures are explicitly simulated fixture accounting, not provider usage.
See [`artifacts/prompt_comparison.csv`](artifacts/prompt_comparison.csv) and
[`artifacts/promotion_decision.json`](artifacts/promotion_decision.json).

Inspect the comparison and trace artifacts:

```powershell
uv run mlflow ui --backend-store-uri sqlite:///artifacts/runtime/mlflow.db --port 5001 --workers 1
```

## Monitoring and regression strategy

`data/golden_cases.json` is the fixed regression set. Each query has an approved reference,
required facts, and relevant evidence/error. Every prompt reruns the identical cases. Two gates
are evaluated per response:

- reference correctness: all material required facts remain present;
- groundedness/safety: the response cites available evidence or safely handles absent evidence.

A prompt is promoted only at `pct_tests_passed == 100`; a failure is treated as a blocking
regression. The failing v2 case was `tool_failure`: it avoided inventing a deadline, but did not
tell the user that policy search was unavailable. Reading the output agrees with the verdict, so
the judge signal passes the manual sanity check. Version 3 explains the outage and offers retry or
human handover.

Evidently produces an HTML report per version with response descriptors and a concision test:

- [`artifacts/prompt_v1_regression_report.html`](artifacts/prompt_v1_regression_report.html)
- [`artifacts/prompt_v2_regression_report.html`](artifacts/prompt_v2_regression_report.html)
- [`artifacts/prompt_v3_regression_report.html`](artifacts/prompt_v3_regression_report.html)

The default judge is deterministic so CI is reproducible. `evaluation.live_llm_judge()` provides
the assignment's native Evidently `LLMEval` path using two `BinaryClassificationPromptTemplate`
judges (correctness and groundedness). To authorize paid calls, set `OPENAI_API_KEY` and
`RUN_LIVE_LLM_JUDGE=1`, then call that function with the response dataframe. Live judge output
must be manually reviewed because an LLM judge can be biased or wrong; it does not replace the
deterministic promotion gate.

## Workflow and layout

```text
golden set → run prompt/config → record full traces → two regression checks
           → Evidently report + MLflow metrics/artifacts → 100% promotion gate
```

- `prompts/`: three explicit prompt versions
- `data/golden_cases.json`: fixed reference test set
- `src/agent_mlops/agent.py`: versioned bounded-agent fixture and trace schema
- `src/agent_mlops/evaluation.py`: deterministic and optional live Evidently judges
- `src/agent_mlops/experiments.py`: MLflow comparison and promotion
- `tests/`: monotonic improvement, trace completeness, and failure-safety checks
