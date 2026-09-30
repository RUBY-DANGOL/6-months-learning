import ast
import operator
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from . import rag

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

SPECS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search the indexed document collection and return matching passages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search phrase"},
                    "top_k": {"type": "integer", "minimum": 1, "maximum": 10},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Exact arithmetic. Required for any multiplication, division, percentage or total; never estimate these yourself. Example expression: '1024 * 0.75'.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "current_time",
            "description": "Current date and time for an IANA timezone.",
            "parameters": {
                "type": "object",
                "properties": {"timezone": {"type": "string", "default": "UTC"}},
            },
        },
    },
]


def _evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
        return OPERATORS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
        return OPERATORS[type(node.op)](_evaluate(node.operand))
    raise ValueError("unsupported expression")


def calculate(expression: str) -> dict:
    try:
        return {"expression": expression, "result": _evaluate(ast.parse(expression, mode="eval").body)}
    except (SyntaxError, ValueError, ZeroDivisionError, TypeError, OverflowError) as exc:
        return {"expression": expression, "error": str(exc)}


def current_time(timezone: str = "UTC") -> dict:
    try:
        zone = ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError):
        return {"error": f"unknown timezone: {timezone}"}
    now = datetime.now(zone)
    return {"timezone": timezone, "iso": now.isoformat(timespec="seconds"), "weekday": now.strftime("%A")}


async def search_knowledge_base(query: str, top_k: int = 4) -> dict:
    hits = await rag.search(query, top_k)
    return {"query": query, "matches": hits}


async def dispatch(name: str, arguments: dict) -> dict:
    if name == "search_knowledge_base":
        return await search_knowledge_base(**arguments)
    if name == "calculate":
        return calculate(**arguments)
    if name == "current_time":
        return current_time(**arguments)
    return {"error": f"unknown tool: {name}"}


def demo():
    assert calculate("2 + 3 * 4")["result"] == 14
    assert calculate("(10 - 4) / 3")["result"] == 2
    assert "error" in calculate("__import__('os').system('ls')")
    assert "error" in calculate("1/0")
    assert current_time("UTC")["weekday"]
    assert "error" in current_time("Mars/Olympus")
    print("tools ok")


if __name__ == "__main__":
    demo()
