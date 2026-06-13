import subprocess
from dataclasses import dataclass


@dataclass
class QueryResult:
    success: bool
    stdout: str
    stderr: str
    return_code: int


def run_sql(sql: str, db_name: str = "mydb", container: str = "mydb") -> QueryResult:
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
    completed = subprocess.run(
        command,
        input=sql,
        text=True,
        capture_output=True,
        check=False,
    )
    return QueryResult(
        success=completed.returncode == 0,
        stdout=completed.stdout,
        stderr=completed.stderr,
        return_code=completed.returncode,
    )
