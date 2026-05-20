import subprocess
from dataclasses import dataclass


@dataclass
class QueryResult:
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time: float = 0.0


def run_sql(sql: str, db_name: str = "mydb", container: str = "mydb") -> QueryResult:
    import time
    command = [
        "docker",
        "exec",
        "-i",
        container,
        "psql",
        "-U",
        "postgres",
        "-d",
        db_name,
        "-v",
        "ON_ERROR_STOP=1",
        "-A",
        "-t",
        "-F",
        "\t",
    ]
    start = time.time()
    completed = subprocess.run(
        command,
        input=sql,
        text=True,
        capture_output=True,
        check=False,
    )
    elapsed = time.time() - start
    return QueryResult(
        success=completed.returncode == 0,
        stdout=completed.stdout,
        stderr=completed.stderr,
        return_code=completed.returncode,
        execution_time=round(elapsed, 4),
    )
