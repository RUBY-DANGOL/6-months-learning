import json
import time
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def ensure_log_dir():
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_execution(
    question: str,
    sql: str,
    status: str,
    execution_time: float | None = None,
    error: str | None = None,
    retries: int = 0,
    result_rows: int | None = None,
):
    ensure_log_dir()
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "question": question,
        "sql": sql,
        "status": status,
        "execution_time": execution_time,
        "error": error,
        "retries": retries,
        "result_rows": result_rows,
    }
    log_path = LOG_DIR / "agent.log"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
