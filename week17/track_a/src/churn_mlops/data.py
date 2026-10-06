"""Dataset acquisition and strict Telco Churn cleaning."""

from __future__ import annotations

import urllib.request
from pathlib import Path

import pandas as pd

from .config import DATA_DIR

DATA_URL = (
    "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/"
    "master/data/Telco-Customer-Churn.csv"
)
DATA_FILE = DATA_DIR / "Telco-Customer-Churn.csv"
TARGET = "Churn"


def download_dataset(path: Path = DATA_FILE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        urllib.request.urlretrieve(DATA_URL, path)
    return path


def load_data(path: Path | None = None) -> tuple[pd.DataFrame, pd.Series]:
    frame = pd.read_csv(path or download_dataset())
    required = {"customerID", "tenure", "MonthlyCharges", "TotalCharges", TARGET}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
    frame["TotalCharges"] = pd.to_numeric(frame["TotalCharges"], errors="coerce")
    frame["TotalCharges"] = frame["TotalCharges"].fillna(frame["TotalCharges"].median())
    y = frame.pop(TARGET).map({"No": 0, "Yes": 1})
    if y.isna().any():
        raise ValueError("Churn must contain only Yes/No values")
    X = frame.drop(columns=["customerID"])
    return X, y.astype(int)

