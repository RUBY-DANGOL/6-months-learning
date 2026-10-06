"""Small deterministic adapter around the W16 bounded-agent behavior.

The fixture policy makes prompt-version effects repeatable. Every decision and tool result is
still recorded in the same trace schema used by a live agent.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Version:
    name: str
    top_k: int
    max_iterations: int
    temperature: float


VERSIONS = [
    Version("prompt_v1", top_k=1, max_iterations=2, temperature=0.2),
    Version("prompt_v2", top_k=2, max_iterations=3, temperature=0.0),
    Version("prompt_v3", top_k=3, max_iterations=5, temperature=0.0),
]


def _step(trace: list[dict], number: int, decision: str, reason: str,
          tool: str | None = None, args: dict | None = None,
          result: object | None = None) -> None:
    trace.append({"step": number, "decision": decision, "reason": reason,
                  "tool": tool, "args": args, "raw_result": result})


def run_case(case: dict, version: Version) -> dict:
    trace: list[dict] = []
    query = case["query"]
    evidence = case.get("evidence", [])[:version.top_k]
    if version.name == "prompt_v1":
        if case["id"] == "refund_timing":
            answer = "Refunds normally arrive soon."
            _step(trace, 1, "answer", "The generic prompt allows an early answer without evidence.")
            status = "success"
        elif case["id"] == "tool_failure":
            _step(trace, 1, "search", "Need the return policy.", "search_policy",
                  {"query": "return deadline", "top_k": 1}, {"error": "TimeoutError"})
            answer = "Returns must be requested within 30 days."
            _step(trace, 2, "answer", "Guessed after the tool failure.")
            status = "max_iterations"
        elif not evidence:
            answer = "Please provide more details."
            _step(trace, 1, "clarify", "The object of the request is ambiguous.")
            status = "success"
        else:
            _step(trace, 1, "search", "Find a related policy.", "search_policy",
                  {"query": query, "top_k": 1}, evidence)
            answer = evidence[0]["text"]
            _step(trace, 2, "answer", "The result looks sufficient, so stop.")
            status = "success"
    elif version.name == "prompt_v2":
        if case.get("tool_error"):
            _step(trace, 1, "search", "Policy evidence is required.", "search_policy",
                  {"query": "return deadline", "top_k": 2}, {"error": case["tool_error"]})
            answer = "I cannot confirm the deadline; contact support."
            _step(trace, 2, "answer", "Avoided guessing, but did not identify the unavailable tool.")
            status = "success"
        elif not evidence:
            answer = "Please clarify what you want to change."
            _step(trace, 1, "clarify", "No policy can be selected until the object is known.")
            status = "success"
        else:
            _step(trace, 1, "search", "Search is mandatory before answering.", "search_policy",
                  {"query": query, "top_k": 2}, evidence)
            answer = f"{evidence[0]['text']} [{evidence[0]['source']}]"
            _step(trace, 2, "answer", "Evidence directly answers the question and has a source.")
            status = "success"
    else:
        if case.get("tool_error"):
            _step(trace, 1, "search", "A deadline requires exact policy evidence.", "search_policy",
                  {"query": "return deadline", "top_k": 3}, {"error": case["tool_error"]})
            answer = ("I cannot verify the return deadline because policy search is unavailable; "
                      "please try later or contact a human advisor.")
            _step(trace, 2, "clarify", "Tool failure prevents a grounded answer; disclose and hand over.")
            status = "success"
        elif not evidence:
            answer = "Please clarify whether you mean an order, delivery address, account, or subscription."
            _step(trace, 1, "clarify", "The pronoun has multiple policy interpretations.")
            status = "success"
        else:
            _step(trace, 1, "search", "Get exact evidence before making a claim.", "search_policy",
                  {"query": query, "top_k": 3}, evidence)
            quote = evidence[0]["text"]
            answer = f"{quote} [{evidence[0]['source']}]"
            _step(trace, 2, "answer", "The exact quote is visible and supports the full answer.")
            status = "success"
    return {"case_id": case["id"], "query": query, "reference": case["reference"],
            "response": answer, "trace": trace, "iterations": len(trace),
            "termination_reason": status, "simulated_tokens": 55 * len(trace)}

