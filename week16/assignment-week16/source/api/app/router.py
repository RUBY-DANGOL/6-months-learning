import json
import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

from .config import settings

log = logging.getLogger("assistant.router")

_session: ort.InferenceSession | None = None
_tokenizer: Tokenizer | None = None
_meta: dict = {}
_labels: list[str] = []


@dataclass
class Route:
    agent: str | None
    confidence: float
    energy: float
    gated: bool
    loaded: bool


def load() -> bool:
    global _session, _tokenizer, _meta, _labels
    if _session is not None:
        return True
    directory = Path(settings.router_model_dir)
    weights = directory / "model.int8.onnx"
    if not weights.exists():
        weights = directory / "model.onnx"
    if not weights.exists() or not (directory / "tokenizer.json").exists():
        log.warning("router model not found in %s; every message is treated as in scope", directory)
        return False

    options = ort.SessionOptions()
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    options.intra_op_num_threads = settings.router_threads
    _session = ort.InferenceSession(str(weights), options, providers=["CPUExecutionProvider"])
    _tokenizer = Tokenizer.from_file(str(directory / "tokenizer.json"))
    _labels = json.loads((directory / "labels.json").read_text())
    meta_file = directory / "router.json"
    _meta = json.loads(meta_file.read_text()) if meta_file.exists() else {}
    _tokenizer.enable_truncation(_meta.get("max_length", 64))
    _tokenizer.enable_padding()
    log.info("router loaded from %s with %d agents", weights.name, len(_labels))
    return True


def threshold() -> float | None:
    return settings.energy_threshold


def suggested_threshold() -> float | None:
    return _meta.get("abstain", {}).get("energy_threshold")


def classify(texts: list[str]) -> list[Route]:
    if not load():
        return [Route(None, 0.0, 0.0, False, False) for _ in texts]

    encodings = _tokenizer.encode_batch(texts)
    logits = _session.run(
        None,
        {
            "input_ids": np.array([e.ids for e in encodings], dtype=np.int64),
            "attention_mask": np.array([e.attention_mask for e in encodings], dtype=np.int64),
        },
    )[0]

    top = logits.max(axis=1, keepdims=True)
    shifted = np.exp(logits - top)
    energies = (top + np.log(shifted.sum(axis=1, keepdims=True))).ravel()
    probs = shifted / shifted.sum(axis=1, keepdims=True)
    limit = threshold()

    routes = []
    for row, score, confidence in zip(logits, energies, probs):
        gated = limit is not None and score < limit
        best = int(row.argmax())
        routes.append(
            Route(
                agent=None if gated else _labels[best],
                confidence=round(float(confidence[best]), 4),
                energy=round(float(score), 3),
                gated=gated,
                loaded=True,
            )
        )
    return routes


def route(text: str) -> Route:
    return classify([text])[0]


def info() -> dict:
    if not load():
        return {"loaded": False}
    return {
        "loaded": True,
        "agents": _labels,
        "energy_gate": threshold(),
        "suggested_energy_gate": suggested_threshold(),
        "metrics": _meta.get("metrics", {}),
        "calibration": _meta.get("abstain", {}),
    }
