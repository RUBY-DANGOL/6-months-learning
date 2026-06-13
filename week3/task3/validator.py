import re

FORBIDDEN_TOKENS = {
    "delete",
    "drop",
    "update",
    "insert",
    "alter",
    "create",
    "truncate",
}


def strip_leading_comments(sql: str) -> str:
    lines = []
    for line in sql.splitlines():
        if line.strip().startswith("--"):
            continue
        lines.append(line)
    return "\n".join(lines)


def validate_select_only(sql: str) -> tuple[bool, str]:
    cleaned = strip_leading_comments(sql).strip()
    if not cleaned:
        return False, "Empty SQL"

    lowered = re.sub(r"\s+", " ", cleaned).strip().lower()
    if not lowered.startswith("select"):
        return False, "Only SELECT queries are allowed"

    tokens = set(re.findall(r"[a-zA-Z_]+", lowered))
    forbidden = tokens.intersection(FORBIDDEN_TOKENS)
    if forbidden:
        return False, f"Forbidden tokens present: {', '.join(sorted(forbidden))}"

    return True, "ok"
