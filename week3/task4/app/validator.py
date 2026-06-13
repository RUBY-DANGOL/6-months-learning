import re

FORBIDDEN_TOKENS = {
    "delete", "drop", "update", "insert",
    "alter", "create", "truncate", "replace",
    "execute", "call", "merge",
}

FORBIDDEN_KEYWORDS = {
    "pg_sleep", "pg_exec", "xp_cmdshell",
    "COPY", "\\copy",
}


def strip_leading_comments(sql: str) -> str:
    lines = []
    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.startswith("--") or stripped.startswith("//"):
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

    if lowered.count("select") > 1 and "union" not in lowered:
        return False, "Multiple SELECT statements detected"

    if ";" in lowered:
        parts = lowered.split(";")
        non_empty = [p.strip() for p in parts if p.strip()]
        if len(non_empty) > 1:
            return False, "Multiple SQL statements detected (semicolons)"

    tokens = set(re.findall(r"[a-zA-Z_]+", lowered))
    forbidden = tokens.intersection(FORBIDDEN_TOKENS)
    if forbidden:
        return False, f"Forbidden tokens present: {', '.join(sorted(forbidden))}"

    for kw in FORBIDDEN_KEYWORDS:
        if kw.lower() in lowered:
            return False, f"Forbidden keyword present: {kw}"

    return True, "ok"
