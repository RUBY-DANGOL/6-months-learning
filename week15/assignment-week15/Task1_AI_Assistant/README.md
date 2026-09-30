# Task 1 - AI Assistant

## What it is

A customer support assistant for an online shop. Each message is:

1. routed to one of 11 support agents (account, refund, delivery, ...) by a DistilBERT classifier
2. matched against a policy knowledge base using vector search (RAG)
3. answered by a locally running Qwen2.5 model, returned as validated JSON with citations

The model can also call tools: `calculate`, `current_time` and `search_knowledge_base`.

Stack: FastAPI, LiteLLM, Qdrant (vectors), Redis (cache), Streamlit (UI), Ollama (model server), Docker.

## Files

| File | |
| --- | --- |
| `source/` | source code |
| `Dockerfile` | image for the assistant service (same as `source/api/Dockerfile`) |
| `architecture-diagram.png` | architecture diagram |

## Run

Needs Docker Desktop and [Ollama](https://ollama.com/download).

```
ollama pull qwen2.5:1.5b
cd source
cp .env.example .env
docker compose up -d --build
```

Wait about a minute, then open:

- UI: http://localhost:8501
- API docs: http://localhost:8080/docs

Check everything is up:

```
curl http://localhost:8080/readyz
```

Run the built-in tests:

```
docker compose exec api python selftest.py
```

Stop:

```
docker compose down
```

## Notes

- A GPU is not required. Ollama uses one if present, otherwise CPU (slower).
- The first reply after start takes about 10 seconds while the model loads.
- The compose file also contains a vLLM service (`docker compose --profile gpu up`) for Linux machines with the NVIDIA container runtime. It did not start on the Windows development laptop because CUDA could not initialise inside WSL2, so Ollama is the default and is what was tested.
