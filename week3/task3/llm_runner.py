import argparse
import json
from pathlib import Path

from executor import execute_with_retry
from validator import validate_select_only

ROOT = Path(__file__).resolve().parents[1]
TASK2 = ROOT / "task2"
TASK3 = ROOT / "task3"

DECOMPOSITIONS_PATH = TASK2 / "decompositions.json"
LOG_PATH = TASK3 / "logs" / "execution.log"

PROMPTS_DIR = TASK3 / "prompts"
PROMPT_EXTRACT = PROMPTS_DIR / "01_extract_decomposition.txt"
PROMPT_SQL = PROMPTS_DIR / "02_generate_sql.txt"
PROMPT_FIX = PROMPTS_DIR / "03_fix_sql.txt"


def load_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def prompt_user(title: str, content: str) -> str:
    print("\n" + "=" * 80)
    print(title)
    print("-" * 80)
    print(content)
    print("-" * 80)
    return input("Paste response and press Enter:\n").strip()


def run_manual(question: str, schema_hint: str) -> tuple[dict, str]:
    extract_template = load_prompt(PROMPT_EXTRACT)
    extract_prompt = extract_template.replace(
        "Question: \"Show all orders placed by customers in Germany\"",
        f"Question: \"{question}\"",
    ).replace(
        "Schema (tables/columns):\n- customers(customerNumber, customerName, country)\n- orders(orderNumber, orderDate, customerNumber)",
        schema_hint,
    )
    decomposition_raw = prompt_user("Prompt 1: Extract Decomposition", extract_prompt)
    decomposition = json.loads(decomposition_raw)

    sql_template = load_prompt(PROMPT_SQL)
    sql_prompt = sql_template.replace(
        "Decomposition JSON:\n{\n  \"intent\": \"Retrieve orders for customers in Germany\",\n  \"tables\": [\"orders\", \"customers\"],\n  \"columns\": [\"orderNumber\", \"orderDate\", \"customerName\"],\n  \"filters\": [\"customers.country = 'Germany'\"],\n  \"joins\": [\"customers.customerNumber = orders.customerNumber\"]\n}",
        "Decomposition JSON:\n" + json.dumps(decomposition, indent=2),
    )
    sql = prompt_user("Prompt 2: Generate SQL", sql_prompt)
    return decomposition, sql


def fix_sql_manual(sql: str, error: str) -> str:
    fix_template = load_prompt(PROMPT_FIX)
    fix_prompt = fix_template.replace(
        "SQL:\nSELECT customers.country, COUNT(*) FROM offices GROUP BY customers.country;",
        "SQL:\n" + sql,
    ).replace(
        "ERROR: column \"customers\" does not exist",
        error.strip() or "ERROR: unknown",
    )
    return prompt_user("Prompt 3: Fix SQL", fix_prompt)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run optional LLM prompt-chaining mode (manual input)")
    parser.add_argument("--limit", type=int, default=1, help="Number of questions to process")
    args = parser.parse_args()

    decompositions = json.loads(DECOMPOSITIONS_PATH.read_text(encoding="utf-8"))

    for item in decompositions[: args.limit]:
        question = item["question"]
        schema_hint = "Schema (tables/columns):\n" + "\n".join(
            [f"- {table}(...)" for table in item.get("tables", [])]
        )
        decomposition, sql = run_manual(question, schema_hint)

        valid, reason = validate_select_only(sql)
        if not valid:
            print(f"Blocked (not SELECT-only): {reason}")
            continue

        outcome = execute_with_retry(sql, LOG_PATH, item["id"], question)
        if outcome.success:
            print("Execution success")
            continue

        fixed = fix_sql_manual(sql, outcome.stderr)
        valid, reason = validate_select_only(fixed)
        if not valid:
            print(f"Blocked after fix (not SELECT-only): {reason}")
            continue

        retry_outcome = execute_with_retry(fixed, LOG_PATH, item["id"], question)
        print("Retry success" if retry_outcome.success else "Retry failed")


if __name__ == "__main__":
    main()
