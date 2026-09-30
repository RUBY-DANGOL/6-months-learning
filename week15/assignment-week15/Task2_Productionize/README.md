# Task 2 - Productionize the Model

## What it is

I used model from assignment of week 14 (a DistilBERT classifier that routes customer messages to one of 11 support agents) turned into a production service inside the Task 1 assistant.

What was done to it:

- exported to ONNX and quantised to INT8 (`source/ml/router.py`)
- served on CPU inside the API on every request (`source/api/app/router.py`)
- wrapped with a web UI, caching, rate limiting, retries, a fallback provider, a circuit breaker and graceful degradation
- packaged with Docker Compose

Results on the 2,688-message test set:

| | Accuracy | Macro-F1 | Latency | Size |
| --- | --- | --- | --- | --- |
| ONNX FP32 | 0.9996 | 0.9997 | 9.8 ms | 268 MB |
| ONNX INT8 | 0.9996 | 0.9997 | 3.9 ms | 67 MB |

Same accuracy, 2.5x faster, 4x smaller, and no GPU needed (week 14 was 12 ms on a GPU).

Serving numbers with the Qwen2.5 1.5B model on an RTX 3060 laptop: first token in 421 ms, median reply 0.7 s, 3 requests/second at concurrency 4, cached replies in 6 ms.

## Files

| File | |
| --- | --- |
| `source/` | updated source code |
| `docker-compose.yml` | Docker Compose configuration (same as `source/docker-compose.yml`) |
| `architecture-diagram.png` | architecture diagram |
| `router-evaluation.json` | metrics written by the export script |
| `benchmark-results.txt` | benchmark output |

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

Useful endpoints:

- `POST /route` - the routing model on its own
- `POST /chat` - full answer as JSON
- `POST /chat/stream` - streamed answer
- `POST /chat/batch` - several messages at once
- `GET /readyz`, `GET /stats` - health and metrics

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
- On free-form messages the router is less accurate than on the test set (about 63% on 35 hand-written examples), so the retrieved policy's category is cross-checked against it and disagreements are logged. This is the drift monitoring the week 14 recommendation asked for.
- The 1.5B language model is not reliable at arithmetic even with the `calculate` tool; a real system should never let it compute refund amounts.
- vLLM is included in the compose file (`--profile gpu`) for Linux machines but could not run on the Windows development laptop (CUDA inside WSL2 failed), so Ollama is the default and is what was tested.
