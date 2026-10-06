"""Thin FastAPI wrapper around the registry champion."""

from functools import lru_cache
from typing import Any

import mlflow
import mlflow.pyfunc
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import MODEL_NAME, TRACKING_URI

app = FastAPI(title="Telco Churn API", version="1.0.0")


class PredictionRequest(BaseModel):
    records: list[dict[str, Any]] = Field(min_length=1, max_length=1000)


@lru_cache(maxsize=1)
def get_model():
    mlflow.set_tracking_uri(TRACKING_URI)
    return mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}@champion")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model": f"{MODEL_NAME}@champion"}


@app.post("/predict")
def predict(payload: PredictionRequest) -> dict:
    try:
        values = get_model().predict(pd.DataFrame(payload.records))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Prediction failed: {exc}") from exc
    return {"predictions": [int(value) for value in values]}

