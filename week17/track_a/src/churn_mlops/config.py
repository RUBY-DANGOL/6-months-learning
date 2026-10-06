from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
ARTIFACT_DIR = ROOT / "artifacts"
RUNTIME_DIR = ARTIFACT_DIR / "runtime"
DB_PATH = RUNTIME_DIR / "mlflow.db"
TRACKING_URI = f"sqlite:///{DB_PATH.as_posix()}"
EXPERIMENT = "telco-churn-model-comparison"
MODEL_NAME = "TelcoChurnClassifier"
RANDOM_STATE = 42


def ensure_directories() -> None:
    for path in (DATA_DIR, ARTIFACT_DIR, RUNTIME_DIR):
        path.mkdir(parents=True, exist_ok=True)

