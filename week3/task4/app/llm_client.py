import json
import os
import re

SCHEMA_TABLES = {
    "customers": ["customerNumber", "customerName", "contactLastName", "contactFirstName", "phone", "addressLine1", "addressLine2", "city", "state", "postalCode", "country", "salesRepEmployeeNumber", "creditLimit"],
    "orders": ["orderNumber", "orderDate", "requiredDate", "shippedDate", "status", "comments", "customerNumber"],
    "orderdetails": ["orderNumber", "productCode", "quantityOrdered", "priceEach", "orderLineNumber"],
    "products": ["productCode", "productName", "productLine", "productVendor", "productDescription", "quantityInStock", "buyPrice", "MSRP"],
    "productlines": ["productLine", "textDescription", "htmlDescription", "image"],
    "employees": ["employeeNumber", "lastName", "firstName", "extension", "email", "officeCode", "reportsTo", "jobTitle"],
    "offices": ["officeCode", "city", "phone", "addressLine1", "addressLine2", "state", "country", "postalCode", "territory"],
    "payments": ["customerNumber", "checkNumber", "paymentDate", "amount"],
}

SCHEMA_TEXT = "\n".join(
    f"- {table}({', '.join(cols)})"
    for table, cols in SCHEMA_TABLES.items()
)

COLUMN_TO_TABLE: dict[str, str] = {}
for table, cols in SCHEMA_TABLES.items():
    for col in cols:
        COLUMN_TO_TABLE[col] = table

TABLE_ALIASES = {
    "customer": "customers",
    "order": "orders",
    "orderdetail": "orderdetails",
    "product": "products",
    "productline": "productlines",
    "employee": "employees",
    "office": "offices",
    "payment": "payments",
}

JOIN_MAP: dict[tuple[str, str], str] = {
    ("orders", "customers"): '"orders"."customerNumber" = "customers"."customerNumber"',
    ("customers", "orders"): '"customers"."customerNumber" = "orders"."customerNumber"',
    ("orders", "orderdetails"): '"orders"."orderNumber" = "orderdetails"."orderNumber"',
    ("orderdetails", "orders"): '"orderdetails"."orderNumber" = "orders"."orderNumber"',
    ("orderdetails", "products"): '"orderdetails"."productCode" = "products"."productCode"',
    ("products", "orderdetails"): '"products"."productCode" = "orderdetails"."productCode"',
    ("products", "productlines"): '"products"."productLine" = "productlines"."productLine"',
    ("productlines", "products"): '"productlines"."productLine" = "products"."productLine"',
    ("customers", "employees"): '"customers"."salesRepEmployeeNumber" = "employees"."employeeNumber"',
    ("employees", "customers"): '"employees"."employeeNumber" = "customers"."salesRepEmployeeNumber"',
    ("employees", "offices"): '"employees"."officeCode" = "offices"."officeCode"',
    ("offices", "employees"): '"offices"."officeCode" = "employees"."officeCode"',
    ("customers", "payments"): '"customers"."customerNumber" = "payments"."customerNumber"',
    ("payments", "customers"): '"payments"."customerNumber" = "customers"."customerNumber"',
}

AGG_KEYWORDS = {
    "count": "COUNT",
    "number of": "COUNT",
    "how many": "COUNT",
    "sum": "SUM",
    "total": "SUM",
    "average": "AVG",
    "avg": "AVG",
    "mean": "AVG",
    "maximum": "MAX",
    "max": "MAX",
    "minimum": "MIN",
    "min": "MIN",
}

TABLE_KEYWORDS: dict[str, list[str]] = {
    "customers": ["customer", "client"],
    "orders": ["order", "placed"],
    "orderdetails": ["order detail", "ordered", "quantity", "order line"],
    "products": ["product", "item"],
    "productlines": ["product line", "category"],
    "employees": ["employee", "staff", "sales rep", "representative", "manager"],
    "offices": ["office", "branch", "location"],
    "payments": ["payment", "check", "transaction"],
}

KNOWN_COUNTRIES = {"USA", "France", "Germany", "UK", "Australia", "Japan", "Spain", "Italy", "Canada", "China", "India", "Brazil", "Netherlands", "Switzerland", "Sweden", "Denmark", "Norway", "Finland", "Belgium", "Austria", "Ireland", "Portugal", "Greece", "Poland", "Czech Republic", "Hungary", "Romania", "Russia", "Turkey", "Israel", "UAE", "Saudi Arabia", "South Africa", "Egypt", "Nigeria", "Kenya", "Argentina", "Chile", "Colombia", "Mexico", "New Zealand", "Singapore", "Malaysia", "Indonesia", "Thailand", "Vietnam", "Philippines", "South Korea", "Taiwan", "Hong Kong"}

STATUS_VALUES = {
    "shipped": "Shipped",
    "pending": "Pending",
    "cancelled": "Cancelled",
    "canceled": "Cancelled",
    "disputed": "Disputed",
    "resolved": "Resolved",
    "in process": "In Process",
    "on hold": "On Hold",
}


def q_ident(name: str) -> str:
    return f'"{name}"'


def q_col(table: str, column: str) -> str:
    return f'"{table}"."{column}"'


def detect_tables(question: str) -> list[str]:
    q = question.lower()
    score: dict[str, int] = {}
    for table, keywords in TABLE_KEYWORDS.items():
        for kw in keywords:
            if kw in q:
                score[table] = score.get(table, 0) + 1
    if not score:
        return ["customers"]
    max_score = max(score.values())
    found = sorted(t for t, s in score.items() if s == max_score)

    if "manager" in q and "employees" not in found:
        found.append("employees")

    return found


def detect_aggregation(question: str) -> str | None:
    q = question.lower()
    for keyword, agg in AGG_KEYWORDS.items():
        if keyword in q:
            return agg
    return None


def _split_camel(name: str) -> list[str]:
    parts = re.findall(r'[A-Z][a-z0-9]*|[a-z0-9]+', name)
    return [p.lower() for p in parts if p]


def detect_columns(question: str, tables: list[str]) -> list[str]:
    q_lower = question.lower()
    q_nospace = q_lower.replace(" ", "")
    candidates = []

    for table in tables:
        for col in SCHEMA_TABLES.get(table, []):
            col_lower = col.lower()
            col_words = re.findall(r'[a-z0-9]+', col_lower)
            score = 0
            for word in col_words:
                if word in q_lower and len(word) > 2:
                    score += 2
            if col_lower in q_lower or col_lower in q_nospace:
                score += 5
            for part in _split_camel(col):
                if part in q_lower and len(part) > 2:
                    score += 1
            if score > 1:
                candidates.append((score, q_col(table, col)))

    candidates.sort(reverse=True)

    if not candidates:
        return ["*"]

    min_score = max(1, candidates[0][0] - 3) if candidates else 1
    selected = [c for s, c in candidates if s >= min_score]
    return selected[:5]


def detect_filters(question: str, tables: list[str]) -> list[str]:
    q = question.lower()
    filters = []

    for country in KNOWN_COUNTRIES:
        if country.lower() in q:
            if "offices" in tables:
                filters.append(f'{q_col("offices", "country")} = \'{country}\'')
            else:
                filters.append(f'{q_col("customers", "country")} = \'{country}\'')
            break

    for raw_status, formatted in STATUS_VALUES.items():
        if raw_status in q:
            filters.append(f'{q_col("orders", "status")} = \'{formatted}\'')
            break

    year_match = re.search(r'\b(20\d{2})\b', q)
    if year_match:
        year = year_match.group(1)
        if "payments" in tables:
            filters.append(f'EXTRACT(YEAR FROM {q_col("payments", "paymentDate")}) = {year}')
        elif "orders" in tables:
            filters.append(f'EXTRACT(YEAR FROM {q_col("orders", "orderDate")}) = {year}')

    return filters


def build_joins(tables: list[str], question: str = "") -> list[str]:
    joins = []
    used_tables = {tables[0]}

    for i in range(1, len(tables)):
        t = tables[i]
        for (a, b), condition in JOIN_MAP.items():
            if a in used_tables and b == t:
                joins.append(condition)
                used_tables.add(t)
                break
            elif b in used_tables and a == t:
                joins.append(condition)
                used_tables.add(t)
                break

    if "manager" in question.lower() and "employees" in tables:
        if "employees" in used_tables:
            joins.append(f'{q_col("employees", "reportsTo")} = {q_col("manager", "employeeNumber")}')

    return joins


def generate_sql_fallback(question: str) -> str:
    tables = detect_tables(question)
    agg = detect_aggregation(question)
    columns = detect_columns(question, tables)
    filters = detect_filters(question, tables)
    joins = build_joins(tables, question)

    select_parts = []
    group_cols = []

    if agg:
        non_star_cols = [c for c in columns if c != "*"]
        if agg == "COUNT" and non_star_cols:
            for col in non_star_cols:
                select_parts.append(col)
                group_cols.append(col.split(" AS ")[0] if " AS " in col else col)
            select_parts.append("COUNT(*) AS count")
        elif agg == "COUNT":
            select_parts.append("COUNT(*) AS count")
        else:
            if non_star_cols:
                cols_for_group = non_star_cols[:-1] if len(non_star_cols) > 1 else []
                for col in cols_for_group:
                    select_parts.append(col)
                    group_cols.append(col.split(" AS ")[0] if " AS " in col else col)
                agg_col = non_star_cols[-1] if non_star_cols else "*"
                select_parts.append(f"{agg}({agg_col}) AS {agg.lower()}")
            else:
                select_parts.append(f"{agg}(*) AS {agg.lower()}")
    else:
        if columns:
            select_parts.extend(columns)
        else:
            select_parts.append("*")

    if not select_parts:
        select_parts.append("*")

    from_table = q_ident(tables[0])
    sql = f"SELECT\n  {',\n  '.join(select_parts)}\nFROM {from_table}"

    used_tables = {tables[0]}
    for join_cond in joins:
        join_table = None
        for t in ["orderdetails", "productlines", "products", "orders", "customers", "employees", "offices", "payments"]:
            if t not in used_tables and t in join_cond:
                join_table = t
                break
        if join_table:
            sql += f"\nJOIN {q_ident(join_table)} ON {join_cond}"
            used_tables.add(join_table)

    if filters:
        sql += "\nWHERE " + " AND ".join(filters)

    if group_cols:
        group_by_cols = []
        for c in group_cols:
            c_stripped = c.replace('"', '')
            group_by_cols.append(q_col(c_stripped.split(".")[0], c_stripped.split(".")[1]) if "." in c_stripped else q_ident(c_stripped))
        sql += "\nGROUP BY " + ", ".join(group_by_cols)

    if not agg and not filters:
        sql += "\nLIMIT 50"

    sql += ";"

    return sql


SYSTEM_PROMPT = f"""You are a PostgreSQL expert. Convert natural language questions into safe SELECT queries.

Database schema:
{SCHEMA_TEXT}

Rules:
- Only generate SELECT queries
- Use explicit JOINs with table aliases
- Use PostgreSQL-compatible syntax
- ALWAYS quote column names with double quotes (e.g., "customers"."customerName")
- Return ONLY the SQL query, no markdown, no explanations
- End with a semicolon
- Use LIMIT when results could be large"""


def call_openai(question: str, api_key: str, model: str = "gpt-4o-mini") -> str | None:
    try:
        import httpx
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            "temperature": 0.1,
        }
        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()
        content = content.removeprefix("```sql").removeprefix("```").strip()
        content = content.removesuffix("```").strip()
        return content
    except Exception as e:
        print(f"[LLM] OpenAI call failed: {e}")
        return None


def generate_sql(question: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        result = call_openai(question, api_key)
        if result:
            return result
        print("[LLM] OpenAI failed, falling back to template-based generator")
    return generate_sql_fallback(question)


def fix_sql_with_llm(sql: str, error: str) -> str | None:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return None

    fix_prompt = f"""The following SQL query failed with an error. Fix it and return only the corrected SQL.

SQL:
{sql}

Error:
{error}

Database schema:
{SCHEMA_TEXT}

Return only the corrected SQL query, no explanations. ALWAYS use double-quoted identifiers like "table"."column"."""
    try:
        import httpx
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a PostgreSQL expert. Fix SQL errors. Always use quoted identifiers."},
                {"role": "user", "content": fix_prompt},
            ],
            "temperature": 0.1,
        }
        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()
        content = content.removeprefix("```sql").removeprefix("```").strip()
        content = content.removesuffix("```").strip()
        return content
    except Exception as e:
        print(f"[LLM] Fix call failed: {e}")
        return None
