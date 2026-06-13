import json
import re
from pathlib import Path

from executor import execute_with_retry
from sql_generator import generate_all
from validator import validate_select_only

ROOT = Path(__file__).resolve().parents[1]
TASK2 = ROOT / "task2"
TASK3 = ROOT / "task3"

DECOMPOSITIONS_PATH = TASK2 / "decompositions.json"
REFERENCE_SQL_PATH = TASK2 / "queries.sql"

GENERATED_SQL_PATH = TASK3 / "generated_queries.sql"
COMPARISON_PATH = TASK3 / "comparison.md"
EVALUATION_PATH = TASK3 / "evaluation.md"
LOG_PATH = TASK3 / "logs" / "execution.log"


def normalize_sql(sql: str) -> str:
    sql = re.sub(r"\s+", " ", sql).strip().lower()
    return sql


def parse_reference_queries(text: str) -> dict:
    pattern = re.compile(r"(?m)^-- Q(\d+):\s*(.+)$")
    matches = list(pattern.finditer(text))
    queries = {}
    for i, match in enumerate(matches):
        qid = int(match.group(1))
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sql = text[start:end].strip()
        queries[qid] = sql
    return queries


def write_generated_sql(queries) -> None:
    blocks = []
    for query in queries:
        blocks.append(f"-- Q{query.id}: {query.question}\n{query.sql}\n")
    GENERATED_SQL_PATH.write_text("\n".join(blocks).strip() + "\n", encoding="utf-8")


def write_comparison(queries, reference) -> None:
    lines = [
        "# Task 3: Generated SQL Comparison",
        "",
        "This report compares auto-generated SQL against Task 2 reference queries.",
        "",
    ]
    for query in queries:
        ref_sql = reference.get(query.id, "")
        is_match = normalize_sql(ref_sql) == normalize_sql(query.sql)
        status = "MATCH" if is_match else "DIFFERENT"
        lines.append(f"## Q{query.id}: {query.question}")
        lines.append("")
        lines.append(f"Status: {status}")
        lines.append("")
        if not is_match:
            lines.append("Generated SQL:")
            lines.append("```")
            lines.append(query.sql)
            lines.append("```")
            lines.append("")
            lines.append("Reference SQL:")
            lines.append("```")
            lines.append(ref_sql)
            lines.append("```")
            lines.append("")

    COMPARISON_PATH.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def write_evaluation(rows) -> None:
    total = len(rows)
    executed = sum(1 for r in rows if r["executed"])
    success = sum(1 for r in rows if r["success"])
    retry_needed = sum(1 for r in rows if r["retry_used"])
    retry_success = sum(1 for r in rows if r["retry_used"] and r["success"])
    match_count = sum(1 for r in rows if r["sql_match"])

    lines = [
        "# Task 3: Evaluation Report",
        "",
        "## Summary",
        f"- Total questions: {total}",
        f"- Executed: {executed}",
        f"- Successful executions: {success}",
        f"- Retry needed: {retry_needed}",
        f"- Retry success: {retry_success}",
        f"- SQL text match vs reference: {match_count}",
        "",
        "## Details",
        "| QID | Executed | Success | Retry | SQL Match | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for row in rows:
        status = "success" if row["success"] else row["status"]
        lines.append(
            f"| {row['id']} | {row['executed']} | {row['success']} | {row['retry_used']} | {row['sql_match']} | {status} |"
        )

    sample_rows = [row for row in rows if row.get("sample_rows")]
    if sample_rows:
        lines.append("")
        lines.append("## Sample Rows")
        lines.append("First 5 successful queries with output (up to 2 rows each).")
        lines.append("")
        for row in sample_rows[:5]:
            lines.append(f"### Q{row['id']}: {row['question']}")
            lines.append("```")
            lines.extend(row["sample_rows"])
            lines.append("```")
            lines.append("")

    EVALUATION_PATH.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> None:
    decompositions = json.loads(DECOMPOSITIONS_PATH.read_text(encoding="utf-8"))
    reference = parse_reference_queries(REFERENCE_SQL_PATH.read_text(encoding="utf-8"))

    queries = generate_all(decompositions)
    write_generated_sql(queries)
    write_comparison(queries, reference)

    rows = []
    for query in queries:
        valid, reason = validate_select_only(query.sql)
        if not valid:
            rows.append(
                {
                    "id": query.id,
                    "question": query.question,
                    "executed": False,
                    "success": False,
                    "retry_used": False,
                    "sql_match": normalize_sql(reference.get(query.id, "")) == normalize_sql(query.sql),
                    "status": f"blocked: {reason}",
                }
            )
            continue

        outcome = execute_with_retry(query.sql, LOG_PATH, query.id, query.question)
        sample_rows = []
        if outcome.success and outcome.stdout:
            sample_rows = [line for line in outcome.stdout.splitlines() if line.strip()][:2]
        rows.append(
            {
                "id": query.id,
                "question": query.question,
                "executed": True,
                "success": outcome.success,
                "retry_used": outcome.retry_used,
                "sql_match": normalize_sql(reference.get(query.id, "")) == normalize_sql(query.sql),
                "status": "success" if outcome.success else "failed",
                "sample_rows": sample_rows,
            }
        )

    write_evaluation(rows)


if __name__ == "__main__":
    main()
