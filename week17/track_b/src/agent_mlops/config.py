from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / "artifacts"
RUNTIME_DIR = ARTIFACT_DIR / "runtime"
PROMPT_DIR = ROOT / "prompts"
CASE_FILE = ROOT / "data" / "golden_cases.json"
TRACKING_URI = f"sqlite:///{(RUNTIME_DIR / 'mlflow.db').as_posix()}"
EXPERIMENT = "shop-assistant-prompt-comparison"


def ensure_directories() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

