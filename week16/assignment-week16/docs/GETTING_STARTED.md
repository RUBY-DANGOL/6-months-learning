# Getting started

## Choose a way to run the project

| Mode | What runs | Requirements | Entry point |
| --- | --- | --- | --- |
| Scripted UI demo | Real Week 16 agent loop with preset model decisions and search results | Python, Streamlit | `source/ui/agent_demo.py` |
| Notebook demo | Same loop and fixtures, with executed outputs | Python, Jupyter, `nbformat`, `nbclient` to re-execute | `agent_demo.ipynb` |
| Evaluation | Same loop and fixtures, assertions and metrics | Python standard library | `source/scripts/evaluate_agent.py` |
| Live stack | Week 15 chat app plus live `/verify` API | Docker engine, Compose, Ollama with `qwen2.5:1.5b` | `source/docker-compose.yml` |

The scripted modes exercise the real `agent.verify` function. The model actions and retrieved text are preset, so they demonstrate control flow and safety checks rather than live answer quality.

## Scripted UI

From `week16/assignment-week16`:

```powershell
python -m pip install -r source/ui/requirements.txt
python -m streamlit run source/ui/agent_demo.py
```

Open the URL printed by Streamlit, usually `http://localhost:8501`. Select a scenario and click **Run agent**. The page shows the question, answer or clarification, status, number of decisions, simulated token count, evidence visible at each decision, and trajectory events. The preset scenarios cover a refined search, clarification, invalid citation, search timeout, and step limit.

The demo was launched locally and its health endpoint returned HTTP 200. Streamlit's app test also exercised the default scenario and displayed `completed`, three decisions, and 126 simulated tokens. This is not a live Ollama/Qdrant run.

## Notebook and evaluation

Open `agent_demo.ipynb` from either its own folder or the repository root. Its code locates the evaluation harness and runs the same cases. To regenerate the Markdown report:

```powershell
python source/scripts/evaluate_agent.py
```

The command writes `evaluation-results.md` and exits with a failure status if a case does not follow its expected behavior.

## Live stack

Install and start Docker Desktop and Ollama, then download the configured model:

```powershell
ollama pull qwen2.5:1.5b
cd source
Copy-Item .env.example .env
docker compose up -d --build
```

Check `http://localhost:8080/readyz` for backend status, open `http://localhost:8501` for the original Week 15 chat UI, and open `http://localhost:8080/docs` for API docs. The Compose API startup loads the router and indexes bundled policy files if the collection is empty. Embedding model setup and first LLM responses can take time.

Invoke the new live endpoint with PowerShell:

```powershell
$body = @{ message = 'Can I cancel an order after it ships?' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri 'http://localhost:8080/verify' -ContentType 'application/json' -Body $body
```

The original Streamlit `source/ui/app.py` calls `/chat`; it does not expose `/verify`. For a visual explanation of the verification loop, use the scripted UI demo. The live stack could not be tested in this workspace because the Docker engine was stopped and `ollama` was unavailable.

Stop the stack with `docker compose down` from `source/`. Named volumes keep Qdrant data and embedding caches; use Compose's volume removal option only if you deliberately want to erase that data.

## Configuration

Copy `source/.env.example` for local overrides. `source/api/app/config.py` defines defaults. The main settings are:

| Variables | Purpose |
| --- | --- |
| `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`, `FALLBACK_MODELS` | LiteLLM provider and fallback chain; defaults target local Ollama |
| `TEMPERATURE`, `TOP_P`, `MAX_TOKENS`, `REQUEST_TIMEOUT`, `NUM_RETRIES` | Model request behavior for the Week 15 chat path; `/verify` fixes temperature to zero and max output to 320 tokens per decision |
| `QDRANT_URL`, `KB_COLLECTION`, `EMBED_MODEL`, `MIN_SCORE`, `TOP_K` | Policy vector retrieval |
| `REDIS_URL`, `CACHE_TTL`, `SEMANTIC_THRESHOLD` | Week 15 exact and semantic chat caching |
| `ROUTER_MODEL_DIR`, `ENERGY_THRESHOLD` | Week 15 classification model and optional abstention threshold |
| `CORPUS_DIR`, `CHUNK_SIZE`, `CHUNK_OVERLAP` | Policy indexing |
| `RATE_LIMIT_PER_MIN` | Per-client Redis-backed API limit |

`/verify` uses the shared model and Qdrant settings but does not use the Week 15 router, chat cache, or chat tools.
