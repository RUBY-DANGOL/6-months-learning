"""Dependency-free behavioral evaluation of the actual agent loop."""
import asyncio
import importlib.util
import json
import sys
import types
from pathlib import Path


def load_agent():
    # The injected modules replace infrastructure only; the agent implementation is real.
    package = types.ModuleType("app")
    package.__path__ = []
    sys.modules["app"] = package
    llm = types.ModuleType("app.llm")
    llm.AllProvidersFailed = type("AllProvidersFailed", (Exception,), {})
    rag = types.ModuleType("app.rag")
    rag.search = None
    sys.modules["app.llm"] = llm
    sys.modules["app.rag"] = rag
    path = Path(__file__).resolve().parents[1] / "api" / "app" / "agent.py"
    spec = importlib.util.spec_from_file_location("app.agent", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CASES = [
    {"name": "refine_search", "question": "Can I cancel after shipping?",
     "decisions": [{"action": "search", "query": "cancel order"},
                   {"action": "search", "query": "cancel shipped order"},
                   {"action": "answer", "answer": "Shipped orders cannot be cancelled.",
                    "citations": [{"source": "CANCEL.md", "quote": "Shipped orders cannot be cancelled."}]}],
     "hits": {"cancel order": [], "cancel shipped order":
              [{"source": "CANCEL.md", "score": .9,
                "text": "Shipped orders cannot be cancelled."}]},
     "expected": "completed", "tools": ["search", "search"], "max_steps": 3},
    {"name": "clarification", "question": "Can I change it?",
     "decisions": [{"action": "clarify", "question": "Which order and what change do you mean?"}],
     "hits": {}, "expected": "needs_clarification", "tools": [], "max_steps": 1},
    {"name": "invented_citation", "question": "Are returns free?",
     "decisions": [{"action": "search", "query": "return fee"},
                   {"action": "answer", "answer": "Returns are always free.",
                    "citations": [{"source": "REFUND.md", "quote": "Returns are always free."}]},
                   {"action": "clarify", "question": "Which product are you returning?"}],
     "hits": {"return fee": [{"source": "REFUND.md", "score": .8,
                              "text": "Return shipping fees depend on the product."}]},
     "expected": "needs_clarification", "tools": ["search"], "max_steps": 3,
     "expected_rejection": True},
    {"name": "injected_tool_failure", "question": "What is the refund deadline?",
     "decisions": [{"action": "search", "query": "refund deadline"},
                   {"action": "clarify", "question": "I cannot check the policy now; can you try later?"}],
     "hits": {}, "fail_query": "refund deadline", "expected": "needs_clarification",
     "tools": ["search"], "max_steps": 2, "expected_error": True},
    {"name": "step_limit", "question": "Check conflicting delivery rules",
     "decisions": [{"action": "search", "query": f"delivery rule {i}"} for i in range(5)],
     "hits": {}, "expected": "incomplete", "tools": ["search"] * 5, "max_steps": 5},
]


async def run_case(agent, case):
    decisions = iter(case["decisions"])
    calls = []

    async def decide(messages):
        # A deterministic model stub still receives the actual compacted prompt.
        assert len(messages) == 2
        return next(decisions), 42, "scripted-model"

    async def search(query, top_k):
        calls.append((query, top_k))
        if query == case.get("fail_query"):
            raise TimeoutError("injected search timeout")
        return case["hits"].get(query, [])

    result = await agent.verify(case["question"], decide=decide, search=search)
    actual_tools = ["search" for x in result.trajectory
                    if x["action"] in ("search", "search_error")]
    correct = (actual_tools == case["tools"] and
               all(k == agent.MAX_HITS and q for q, k in calls))
    completed = result.status == case["expected"]
    checks = (not case.get("expected_rejection") or
              any(x["action"] == "invalid_answer" for x in result.trajectory)) and (
              not case.get("expected_error") or
              any(x["action"] == "search_error" for x in result.trajectory))
    success = correct and completed and checks and result.steps <= case["max_steps"]
    if result.status == "incomplete":
        failure = "hard failure"
    elif success:
        failure = None
    elif any(x["action"].startswith("invalid") for x in result.trajectory):
        failure = "cascading soft failure"
    else:
        failure = "soft failure"
    return {"case": case["name"], "success": success,
            "task_completed": result.status in ("completed", "needs_clarification"),
            "status": result.status,
            "tool_call_correct": correct, "steps": result.steps,
            "tokens": result.tokens, "failure": failure,
            "trajectory": result.trajectory}


async def main():
    agent = load_agent()
    rows = [await run_case(agent, case) for case in CASES]
    report = Path(__file__).resolve().parents[2] / "evaluation-results.md"
    lines = ["# Agent evaluation results", "",
             "Deterministic scripted model and retrieval fixtures; token counts are simulated "
             "usage values, not a measured live-model cost.", "",
             f"Task completion rate: {sum(r['task_completed'] for r in rows)}/{len(rows)}. "
             f"Expected behavior: {sum(r['success'] for r in rows)}/{len(rows)}. "
             f"Tool-call correctness: {sum(r['tool_call_correct'] for r in rows)}/{len(rows)}.", "",
             "| Case | Expected behavior met | Tool call correct | Steps | Tokens | Failure |",
             "| --- | --- | --- | ---: | ---: | --- |"]
    for r in rows:
        lines.append(f"| {r['case']} | {r['success']} | {r['tool_call_correct']} | "
                     f"{r['steps']} | {r['tokens']} | {r['failure'] or '—'} |")
    failures = [f"- {r['case']}: {r['failure']}" for r in rows if r["failure"]]
    lines += ["", "## Failure log", "",
              *(failures or ["No unsuccessful cases in this fixture run."]), "",
              "A hard failure is an incorrect or "
              "unfinished task; a soft failure is a recoverable wrong decision; a cascading "
              "soft failure is a recoverable error that causes subsequent bad decisions.", "",
              "## Injection", "",
              "The `injected_tool_failure` case raises a search timeout. The agent records "
              "`search_error` and asks for clarification instead of inventing a deadline.", "",
              "## Machine readable trajectories", "", "```json",
              json.dumps(rows, indent=2), "```", ""]
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {report}; {sum(r['success'] for r in rows)}/{len(rows)} passed")
    if not all(r["success"] for r in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
