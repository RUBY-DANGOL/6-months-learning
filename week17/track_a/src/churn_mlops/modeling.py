from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass(frozen=True)
class Candidate:
    name: str
    family: str
    params: dict


CANDIDATES = [
    Candidate("logistic_c_0_25", "logistic", {"C": 0.25, "penalty": "l2"}),
    Candidate("logistic_c_1_0", "logistic", {"C": 1.0, "penalty": "l2"}),
    Candidate(
        "random_forest_300_depth_8",
        "random_forest",
        {"n_estimators": 300, "max_depth": 8, "min_samples_leaf": 3},
    ),
]


def make_pipeline(X: pd.DataFrame, candidate: Candidate) -> Pipeline:
    numeric = X.select_dtypes(include="number").columns.tolist()
    categorical = X.select_dtypes(exclude="number").columns.tolist()
    preprocessor = ColumnTransformer(
        [
            ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")),
                                  ("scale", StandardScaler())]), numeric),
            ("categorical", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                                      ("encode", OneHotEncoder(handle_unknown="ignore"))]), categorical),
        ]
    )
    if candidate.family == "logistic":
        estimator = LogisticRegression(
            **candidate.params, class_weight="balanced", max_iter=1500, random_state=42
        )
    else:
        estimator = RandomForestClassifier(
            **candidate.params, class_weight="balanced", n_jobs=-1, random_state=42
        )
    return Pipeline([("preprocess", preprocessor), ("classifier", estimator)])

