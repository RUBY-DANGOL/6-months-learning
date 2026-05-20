import json
import re
import time

from app.database import run_sql
from app.llm_client import generate_sql, fix_sql_with_llm, SCHEMA_TABLES
from app.logger import log_execution
from app.validator import validate_select_only

COLUMN_TO_TABLE: dict[str, str] = {}
for table, cols in SCHEMA_TABLES.items():
    for col in cols:
        COLUMN_TO_TABLE[col] = table

MAX_RETRIES = 3


def extract_error_info(error: str) -> dict:
    info = {"type": "unknown", "column": None, "table": None, "detail": error[:200]}

    col_match = re.search(r'column\s+"([^"]+)"\s+does\s+not\s+exist', error, re.IGNORECASE)
    if col_match:
        info["type"] = "missing_column"
        info["column"] = col_match.group(1)

    rel_match = re.search(r'relation\s+"([^"]+)"\s+does\s+not\s+exist', error, re.IGNORECASE)
    if rel_match:
        info["type"] = "missing_table"
        info["table"] = rel_match.group(1)

    if "ambiguous" in error.lower():
        info["type"] = "ambiguous_column"

    if "syntax error" in error.lower():
        info["type"] = "syntax_error"

    if "does not exist" in error.lower() and not col_match and not rel_match:
        type_match = re.search(r'"([^"]+)"\s+does\s+not\s+exist', error, re.IGNORECASE)
        if type_match:
            info["type"] = "missing_object"
            info["column"] = type_match.group(1)

    return info


def fix_common_errors(sql: str, error: str) -> str | None:
    info = extract_error_info(error)

    if info["type"] == "missing_column":
        col = info["column"]
        if col and "." in col:
            parts = col.split(".")
            wrong_table = parts[0]
            wrong_col = parts[1]
            if wrong_col in COLUMN_TO_TABLE:
                correct_table = COLUMN_TO_TABLE[wrong_col]
                if wrong_table != correct_table:
                    return sql.replace(f'"{wrong_table}"."{wrong_col}"', f'"{correct_table}"."{wrong_col}"')
                    return sql.replace(f"{wrong_table}.{wrong_col}", f"{correct_table}.{wrong_col}")

        if col in COLUMN_TO_TABLE:
            correct_table = COLUMN_TO_TABLE[col]
            for table in SCHEMA_TABLES:
                if table != correct_table and f'"{table}"."{col}"' in sql:
                    return sql.replace(f'"{table}"."{col}"', f'"{correct_table}"."{col}"')

    if info["type"] == "syntax_error":
        if ",\nFROM" in sql.upper() or ",\nfrom" in sql.lower():
            return re.sub(r",\s*\nFROM", "\nFROM", sql, flags=re.IGNORECASE)
        if ",\nfrom" in sql.lower():
            return re.sub(r",\s*\nfrom", "\nfrom", sql, flags=re.IGNORECASE)

    if info["type"] == "ambiguous_column":
        col_pattern = re.compile(r"column reference \"([^\"]+)\" is ambiguous", re.IGNORECASE)
        match = col_pattern.search(error)
        if match:
            col_name = match.group(1)
            if col_name in COLUMN_TO_TABLE:
                table = COLUMN_TO_TABLE[col_name]
                return sql.replace(f'"{col_name}"', f'"{table}"."{col_name}"')

    return None


def parse_result(stdout: str) -> list:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    return lines


def decompose_question(question: str) -> dict:
    q = question.lower()

    intent = "Retrieve data"
    if "count" in q or "how many" in q or "number of" in q:
        intent = "Count records"
    elif "sum" in q or "total" in q:
        intent = "Calculate sum"
    elif "average" in q or "avg" in q:
        intent = "Calculate average"
    elif "max" in q or "maximum" in q:
        intent = "Find maximum"
    elif "min" in q or "minimum" in q:
        intent = "Find minimum"
    elif "list" in q or "show" in q or "get" in q or "find" in q:
        intent = "List records"

    return {
        "question": question,
        "intent": intent,
    }


def process_question(question: str) -> dict:
    start_time = time.time()
    decomposition = decompose_question(question)

    print(f"[Agent] Step 1 — Decomposition: {decomposition['intent']}")

    sql = generate_sql(question)
    print(f"[Agent] Step 2 — Generated SQL:\n{sql}")

    valid, reason = validate_select_only(sql)
    if not valid:
        print(f"[Agent] Step 3 — Validation failed: {reason}")
        log_execution(question, sql, "blocked", error=reason)
        return {
            "status": "error",
            "summary": f"Unsafe query detected: {reason}",
            "sql": sql,
            "result": None,
            "error": reason,
            "execution_time": round(time.time() - start_time, 4),
            "retries": 0,
        }
    print("[Agent] Step 3 — Validation passed")

    last_error = None
    last_sql = sql
    retries = 0

    for attempt in range(MAX_RETRIES + 1):
        print(f"[Agent] Step 4 — Execution attempt {attempt + 1}/{MAX_RETRIES + 1}")
        result = run_sql(last_sql)

        if result.success:
            rows = parse_result(result.stdout)
            elapsed = round(time.time() - start_time, 4)
            print(f"[Agent] Step 4 — Success ({len(rows)} rows in {result.execution_time}s)")

            summary = f"Query executed successfully. Returned {len(rows)} row(s)."

            log_execution(
                question=question,
                sql=last_sql,
                status="success",
                execution_time=result.execution_time,
                result_rows=len(rows),
                retries=retries,
            )

            return {
                "status": "success",
                "sql": last_sql,
                "result": rows,
                "summary": summary,
                "execution_time": result.execution_time,
                "retries": retries,
            }

        last_error = result.stderr
        print(f"[Agent] Step 5 — Execution failed: {last_error[:150]}...")

        if attempt >= MAX_RETRIES - 1:
            break

        fixed = fix_common_errors(last_sql, last_error)
        if not fixed:
            fixed = fix_sql_with_llm(last_sql, last_error)

        if fixed and fixed != last_sql:
            valid2, reason2 = validate_select_only(fixed)
            if valid2:
                last_sql = fixed
                retries += 1
                print(f"[Agent] Step 5 — Retry {retries} with fixed SQL:\n{last_sql}")
                continue
            else:
                print(f"[Agent] Step 5 — Fixed SQL invalid: {reason2}")

        print(f"[Agent] Step 5 — Could not auto-fix, trying different approach...")

        sql2 = generate_sql(question)
        if sql2 and sql2 != last_sql:
            valid3, _ = validate_select_only(sql2)
            if valid3:
                last_sql = sql2
                retries += 1
                print(f"[Agent] Step 5 — Regenerated SQL for retry {retries}:\n{last_sql}")
                continue

        break

    elapsed = round(time.time() - start_time, 4)
    print(f"[Agent] Step 5 — All retries exhausted after {retries} retries")

    log_execution(
        question=question,
        sql=last_sql,
        status="failed",
        execution_time=elapsed,
        error=last_error[:500] if last_error else "Unknown error",
        retries=retries,
    )

    return {
        "status": "failed",
        "sql": last_sql,
        "result": None,
        "summary": "SQL execution failed after retries",
        "error": last_error[:500] if last_error else "SQL execution failed after 3 retries",
        "execution_time": elapsed,
        "retries": retries,
    }
