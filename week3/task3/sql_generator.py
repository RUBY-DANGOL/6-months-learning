import re
from dataclasses import dataclass


@dataclass
class GeneratedQuery:
    id: int
    question: str
    sql: str


SCHEMA_HINTS = {
    "productCode": "products",
    "productName": "products",
    "productLine": "products",
    "quantityInStock": "products",
    "buyPrice": "products",
    "MSRP": "products",
    "productVendor": "products",
    "textDescription": "productlines",
    "htmlDescription": "productlines",
    "image": "productlines",
    "orderNumber": "orders",
    "orderDate": "orders",
    "requiredDate": "orders",
    "shippedDate": "orders",
    "status": "orders",
    "comments": "orders",
    "quantityOrdered": "orderdetails",
    "priceEach": "orderdetails",
    "orderLineNumber": "orderdetails",
    "customerNumber": "customers",
    "customerName": "customers",
    "contactLastName": "customers",
    "contactFirstName": "customers",
    "phone": "customers",
    "addressLine1": "customers",
    "addressLine2": "customers",
    "city": "customers",
    "state": "customers",
    "postalCode": "customers",
    "country": "customers",
    "salesRepEmployeeNumber": "customers",
    "creditLimit": "customers",
    "paymentDate": "payments",
    "amount": "payments",
    "checkNumber": "payments",
    "employeeNumber": "employees",
    "firstName": "employees",
    "lastName": "employees",
    "extension": "employees",
    "email": "employees",
    "officeCode": "offices",
    "territory": "offices",
}


def quote_ident(name: str) -> str:
    return '"' + name + '"'


def quote_qualified(token: str) -> str:
    parts = token.split(".")
    return ".".join(quote_ident(p) for p in parts)


def detect_aggregate(intent: str) -> str | None:
    intent = intent.lower()
    if "count" in intent or "number of" in intent:
        return "COUNT"
    if "sum" in intent or "total" in intent:
        return "SUM"
    if "average" in intent or "avg" in intent:
        return "AVG"
    if "max" in intent:
        return "MAX"
    if "min" in intent:
        return "MIN"
    return None


def needs_group_by(intent: str, columns: list[str]) -> bool:
    intent = intent.lower()
    if "per" in intent or "group" in intent or "grouped" in intent:
        return True
    if len(columns) > 1 and any(keyword in intent for keyword in ["count", "sum", "avg", "average", "max", "min"]):
        return True
    return False


def extract_join_tables(joins: list[str]) -> dict:
    table_cols: dict[str, set[str]] = {}
    token_re = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)")
    for join in joins:
        for table, col in token_re.findall(join):
            table_cols.setdefault(table, set()).add(col)
    return table_cols


def guess_table_for_column(column: str, tables: list[str], joins: list[str]) -> str | None:
    if column in {"managerFirstName", "managerLastName", "managerNumber"}:
        return "manager"

    if column in {"salesRepFirstName", "salesRepLastName"}:
        return "employees" if "employees" in tables else None

    if column in SCHEMA_HINTS and SCHEMA_HINTS[column] in tables:
        return SCHEMA_HINTS[column]

    join_tables = extract_join_tables(joins)
    for table, cols in join_tables.items():
        if column in cols:
            return table

    if len(tables) == 1:
        return tables[0]

    return tables[0] if tables else None


def render_column(column: str, tables: list[str], joins: list[str]) -> str:
    if column == "managerNumber":
        return f'{quote_ident("manager")}.{quote_ident("employeeNumber")} AS {quote_ident("managerNumber")}'
    if column == "managerFirstName":
        return f'{quote_ident("manager")}.{quote_ident("firstName")} AS {quote_ident("managerFirstName")}'
    if column == "managerLastName":
        return f'{quote_ident("manager")}.{quote_ident("lastName")} AS {quote_ident("managerLastName")}'
    if column == "salesRepFirstName":
        return f'{quote_ident("employees")}.{quote_ident("firstName")} AS {quote_ident("salesRepFirstName")}'
    if column == "salesRepLastName":
        return f'{quote_ident("employees")}.{quote_ident("lastName")} AS {quote_ident("salesRepLastName")}'

    if "." in column:
        return quote_qualified(column)

    table = guess_table_for_column(column, tables, joins)
    if table:
        return f"{quote_ident(table)}.{quote_ident(column)}"
    return quote_ident(column)


def render_join_condition(condition: str) -> str:
    token_re = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)")
    return token_re.sub(lambda m: quote_qualified(f"{m.group(1)}.{m.group(2)}"), condition)


def select_distinct(intent: str) -> bool:
    intent = intent.lower()
    return "unique" in intent or "distinct" in intent


def join_type_for_condition(condition: str) -> str:
    if "salesRepEmployeeNumber" in condition:
        return "LEFT JOIN"
    if "reportsTo" in condition:
        return "LEFT JOIN"
    return "JOIN"


def build_sql(item: dict) -> str:
    tables = list(item.get("tables", []))
    joins = list(item.get("joins", []))
    columns = list(item.get("columns", []))
    intent = item.get("intent", "")

    extra_tables = []
    if any("manager." in j for j in joins) and "manager" not in tables:
        extra_tables.append(("employees", "manager"))

    agg = detect_aggregate(intent)
    distinct = select_distinct(intent)
    use_group = needs_group_by(intent, columns)

    select_parts: list[str] = []
    group_cols: list[str] = []

    if agg:
        if agg == "COUNT":
            if use_group:
                group_cols = columns
                for col in group_cols:
                    select_parts.append(render_column(col, tables, joins))
            select_parts.append(f'{agg}(*) AS {quote_ident("count")}' )
        else:
            group_cols = columns[:-1] if use_group else []
            agg_col = columns[-1] if columns else "*"
            for col in group_cols:
                select_parts.append(render_column(col, tables, joins))
            select_parts.append(f'{agg}({render_column(agg_col, tables, joins)}) AS {quote_ident(agg.lower() + "Value")}' )
    else:
        for col in columns:
            select_parts.append(render_column(col, tables, joins))

    from_table = tables[0] if tables else None
    if not from_table:
        raise ValueError("No tables provided")

    used_tables = {from_table}
    join_clauses: list[str] = []

    for join in joins:
        tables_in_join = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\.", join)
        join_table = None
        for t in tables_in_join:
            if t not in used_tables:
                join_table = t
                break
        if join_table is None and tables_in_join:
            join_table = tables_in_join[-1]

        condition = render_join_condition(join)
        if join_table:
            join_keyword = join_type_for_condition(join)
            join_clauses.append(f"{join_keyword} {quote_ident(join_table)} ON {condition}")
            used_tables.add(join_table)

    for base, alias in extra_tables:
        join_clauses.append(
            f"LEFT JOIN {quote_ident(base)} AS {quote_ident(alias)} ON {render_join_condition('employees.reportsTo = manager.employeeNumber')}"
        )

    select_keyword = "SELECT DISTINCT" if distinct else "SELECT"
    select_sql = ",\n  ".join(select_parts) if select_parts else "*"
    sql_lines = [select_keyword, f"  {select_sql}", f"FROM {quote_ident(from_table)}"]
    for clause in join_clauses:
        sql_lines.append(clause)

    if agg and group_cols:
        group_sql = ", ".join(render_column(c, tables, joins).split(" AS ")[0] for c in group_cols)
        sql_lines.append(f"GROUP BY {group_sql}")

    return "\n".join(sql_lines) + ";"


def generate_all(decompositions: list[dict]) -> list[GeneratedQuery]:
    queries: list[GeneratedQuery] = []
    for item in decompositions:
        queries.append(GeneratedQuery(id=item["id"], question=item["question"], sql=build_sql(item)))
    return queries
