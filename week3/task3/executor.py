import json
import re
import time
from dataclasses import dataclass
from pathlib import Path

from database import run_sql


@dataclass
class ExecutionOutcome:
    success: bool
    stdout: str
    stderr: str
    retry_used: bool


def extract_missing_column(error: str) -> str | None:
    match = re.search(r'column "([^"]+)" does not exist', error, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def swap_table(sql: str, column: str, from_table: str, to_table: str) -> str:
    token = f'"{from_table}"."{column}"'
    replacement = f'"{to_table}"."{column}"'
    return sql.replace(token, replacement)


def fix_sql(sql: str, error: str) -> str | None:
    missing_col = extract_missing_column(error)
    if missing_col:
        if missing_col in {"textDescription", "htmlDescription", "image"}:
            if '"products"' in sql and '"productlines"' in sql:
                updated = swap_table(sql, missing_col, "products", "productlines")
                if updated != sql:
                    return updated

        if missing_col in {"city", "country", "phone", "state", "postalCode"}:
            if '"offices"' in sql and '"customers"' in sql:
                updated = swap_table(sql, missing_col, "offices", "customers")
                if updated != sql:
                    return updated
                updated = swap_table(sql, missing_col, "customers", "offices")
                if updated != sql:
                    return updated

    if "syntax error" in error.lower() and ",\nfrom" in sql.lower():
        return re.sub(r",\s*\nFROM", "\nFROM", sql, flags=re.IGNORECASE)

    return None


def execute_with_retry(sql: str, log_path: Path, qid: int, question: str) -> ExecutionOutcome:
    first = run_sql(sql)
    if first.success:
        log_execution(log_path, qid, question, sql, first, retry_used=False)
        return ExecutionOutcome(True, first.stdout, first.stderr, False)

    retry_sql = fix_sql(sql, first.stderr)
    if retry_sql:
        second = run_sql(retry_sql)
        log_execution(log_path, qid, question, retry_sql, second, retry_used=True)
        return ExecutionOutcome(second.success, second.stdout, second.stderr, True)

    log_execution(log_path, qid, question, sql, first, retry_used=False)
    return ExecutionOutcome(False, first.stdout, first.stderr, False)


def log_execution(log_path: Path, qid: int, question: str, sql: str, result, retry_used: bool) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "id": qid,
        "question": question,
        "sql": sql,
        "success": result.success,
        "return_code": result.return_code,
        "stderr": result.stderr.strip(),
        "row_count": len(result.stdout.splitlines()) if result.stdout else 0,
        "retry_used": retry_used,
    }
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
