# File and API reference

All paths in this document are relative to `week16/assignment-week16`.

## Repository files

| Path | Responsibility |
| --- | --- |
| `README.md` | Assignment summary, architecture diagram, and decision rationale |
| `docs/GETTING_STARTED.md` | Run modes, setup, and configuration |
| `docs/ARCHITECTURE.md` | Component and request flows |
| `docs/FILE_AND_API_REFERENCE.md` | This inventory and API reference |
| `agent_demo.ipynb` | Executed notebook showing real loop behavior with scripted fixtures |
| `evaluation-results.md` | Generated deterministic evaluation table and trajectories |
| `source/docker-compose.yml` | API, UI, Qdrant, Redis services; optional trainer and vLLM profiles |
| `source/.env.example` | Example environment overrides |
| `source/.dockerignore`, `source/.gitignore` | Build and repository exclusions |
| `source/api/Dockerfile`, `source/api/requirements.txt` | API container and Python dependencies |
| `source/api/selftest.py` | Original assistant's local unit checks |
| `source/api/app/main.py` | FastAPI startup and HTTP endpoints |
| `source/api/app/agent.py` | Week 16 decision loop, context compaction, citation validation, token and trajectory accounting |
| `source/api/app/schemas.py` | Pydantic request and `/chat` response models |
| `source/api/app/config.py` | Environment-backed settings and defaults |
| `source/api/app/llm.py` | LiteLLM client, provider fallbacks, concurrency limit, circuit breaker, streaming |
| `source/api/app/rag.py` | Document chunking, indexing, Qdrant search |
| `source/api/app/router.py` | ONNX router inference and category metadata |
| `source/api/app/prompts.py` | Original chat instructions and 11 category descriptions |
| `source/api/app/tools.py` | Original chat's calculator, current time, and knowledge-base tools |
| `source/api/app/cache.py` | Redis exact cache and Qdrant semantic cache for `/chat` |
| `source/api/app/ratelimit.py` | Redis-backed per-minute API limit |
| `source/api/app/logging_setup.py` | JSON log formatting |
| `source/ui/app.py`, `source/ui/Dockerfile`, `source/ui/requirements.txt` | Original Streamlit chat UI and container |
| `source/ui/agent_demo.py` | Local interactive scripted demonstration of the Week 16 loop |
| `source/scripts/evaluate_agent.py` | Dependency-free behavioral harness; writes `evaluation-results.md` |
| `source/scripts/bench.py` | Original `/chat` latency, throughput, and streaming benchmark |
| `source/ml/router.py`, `source/ml/Dockerfile`, `source/ml/requirements.txt` | Optional router training/export pipeline and dependencies |
| `source/ml/models/router/*` | Exported ONNX weights, tokenizer, labels, and router metadata |
| `source/corpus/*.md` | Eleven sample policy categories indexed into Qdrant |
| `source/docs/*.png` | Carried-over Week 15 architecture images; the current Week 16 loop diagram is in `README.md` and `docs/ARCHITECTURE.md` |

The policy categories are `ACCOUNT`, `CANCEL`, `CONTACT`, `DELIVERY`, `FEEDBACK`, `INVOICE`, `ORDER`, `PAYMENT`, `REFUND`, `SHIPPING`, and `SUBSCRIPTION`. Files are named after their categories. The router model files are carried over from Week 15; `/verify` retrieves directly and does not classify a question first.

## Python dependency inventory

Versions are pinned in the three `requirements.txt` files except where shown otherwise.

| Environment | Packages and use |
| --- | --- |
| API web | `fastapi==0.115.6`, `uvicorn[standard]==0.34.0`, `pydantic==2.10.4`, `pydantic-settings==2.7.0`, `python-multipart==0.0.20` for HTTP, schemas, environment settings, and uploads |
| API model and retrieval | `litellm==1.57.0` for LLM calls; `qdrant-client[fastembed]==1.12.2` for vector storage and local embeddings; `redis==5.2.1` for cache and rate limit |
| API routing and documents | `onnxruntime==1.20.1`, `numpy==2.1.3`, `tokenizers==0.21.0` for router inference; `pypdf==5.1.0` for PDF extraction |
| API utilities | `httpx==0.27.2` for provider readiness checks; `tzdata==2024.2` for named time zones |
| UI | `streamlit==1.41.1` and `httpx==0.27.2` |
| Optional router training | `torch==2.6.0`, `transformers==4.49.0`, `datasets==3.2.0`, `scikit-learn==1.6.1`, `onnx>=1.17`, `onnxruntime==1.20.1` |

The evaluation harness itself uses only the Python standard library. Re-executing the notebook requires a Jupyter-compatible Python kernel; `nbformat` and `nbclient` were used to validate and execute the checked-in notebook.

## HTTP endpoints

| Method and path | Behavior |
| --- | --- |
| `POST /verify` | Week 16 policy verification loop; takes `ChatRequest.message` and returns an `Outcome` dictionary |
| `POST /chat` | Original routed RAG answer, optional tools, cache, structured `ChatResponse` |
| `POST /chat/stream` | Original answer stream as server-sent events |
| `POST /chat/batch` | Original batch chat replies |
| `POST /route` | Router predictions for messages |
| `POST /ingest` | Index uploaded PDF, Markdown, or text files |
| `POST /ingest/corpus` | Reindex bundled policy directory |
| `GET /healthz` | Basic API process check |
| `GET /readyz` | Model, Redis, router, and indexed-chunk status |
| `GET /stats` | Runtime settings and collection summary |

Example live verification request:

```json
{"message": "Can I cancel an order after it ships?"}
```

An answer includes a validated citation, for example:

```json
{
  "status": "completed",
  "answer": "Example grounded answer",
  "citations": [{"source": "CANCEL.md", "quote": "Exact text visible in the retrieved snippet"}],
  "trajectory": [{"step": 1, "action": "search", "query": "cancel shipped order", "matches": 1}, {"step": 2, "action": "answer"}],
  "tokens": 0,
  "steps": 2,
  "model": "provider model name"
}
```

The example illustrates the response shape; its policy wording and token value are placeholders. FastAPI validates the input with `ChatRequest`, including a nonempty message of at most 8,000 characters. `/verify` does not currently use the other `ChatRequest` options such as `top_k`, `temperature`, or `use_tools`.

## Evaluation cases and interpretation

| Fixture | Intended observation |
| --- | --- |
| `refine_search` | Empty first search leads to a new query, then cited answer |
| `clarification` | Ambiguous customer request leads to a question |
| `invented_citation` | Quote missing from visible evidence is rejected, then clarification |
| `injected_tool_failure` | Injected timeout is logged as `search_error`, then clarification |
| `step_limit` | Five searches end as `incomplete` |

The harness checks expected behavior, search tool selection, nonempty query and `top_k=3`, step count, and token sum. It records each trajectory and classifies incomplete work as a hard failure, a recoverable bad decision as a soft failure, and bad decisions propagated from an earlier recoverable error as a cascading soft failure. The five-decision fixture intentionally ends incomplete: it passes its expected-behavior check but does not count as task completion. Current fixture usage is simulated at 42 tokens per model decision. See `evaluation-results.md` for the generated counts and individual trajectories.

## Current limits

- Live `/verify` has not been exercised in this workspace because Docker and Ollama were unavailable during setup. The scripted notebook, harness, and Streamlit demo were executed.
- The local agent demo presents preset scenarios, not arbitrary customer questions or a live model.
- The original chat UI does not call `/verify`; use the API for live verification.
- Citation validation checks exact source text, not whether the answer's interpretation is correct.
- Qdrant errors caught inside `rag.search` can appear as empty results rather than `search_error` events.
- Token usage is a lower bound when a provider omits usage metadata; no currency cost is computed.
