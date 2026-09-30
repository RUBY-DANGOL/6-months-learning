"""Bounded, model-directed verification over the W15 policy corpus."""

import json
from dataclasses import dataclass, field
from typing import Awaitable, Callable

from . import llm, rag

MAX_STEPS = 5
MAX_HITS = 3
MAX_CHARS_PER_HIT = 650

SYSTEM = """You verify customer-support policy claims against the indexed policy documents.
At each step return ONLY one JSON object with one of these shapes:
{"action":"search","query":"focused policy search phrase"}
{"action":"clarify","question":"one specific question for the customer"}
{"action":"answer","answer":"grounded response","citations":[{"source":"filename","quote":"exact short excerpt"}]}
Search again when evidence is missing, ambiguous, or conflicts. Change the query based on prior results.
Use only visible evidence. Never invent a policy or cite text you have not seen.
If a tool fails, seek other evidence or clarify. If the question cannot be answered safely, clarify.
"""


@dataclass
class Outcome:
    status: str
    answer: str
    citations: list[dict] = field(default_factory=list)
    trajectory: list[dict] = field(default_factory=list)
    tokens: int = 0
    steps: int = 0
    model: str = "none"

    def as_dict(self) -> dict:
        return vars(self)


def _compact(hits: list[dict]) -> list[dict]:
    """Keep only the evidence that the next decision can actually use."""
    seen = set()
    result = []
    for hit in sorted(hits, key=lambda h: h.get("score", 0), reverse=True):
        key = (hit.get("source"), hit.get("text", "")[:MAX_CHARS_PER_HIT])
        if key in seen:
            continue
        seen.add(key)
        result.append({"source": str(hit.get("source", "unknown")),
                       "score": hit.get("score", 0),
                       "text": str(hit.get("text", ""))[:MAX_CHARS_PER_HIT]})
        if len(result) == MAX_HITS:
            break
    return result


def _valid_citations(citations: object, evidence: list[dict]) -> bool:
    if not isinstance(citations, list) or not citations:
        return False
    return all(isinstance(c, dict) and isinstance(c.get("source"), str)
               and isinstance(c.get("quote"), str) and c["quote"].strip()
               and any(c["source"] == h["source"] and c["quote"] in h["text"]
                       for h in evidence) for c in citations)


async def _decide(messages: list[dict]) -> tuple[dict, int, str]:
    response, model = await llm.complete(messages, response_format={"type": "json_object"},
                                         temperature=0, max_tokens=320)
    usage = getattr(response, "usage", None)
    tokens = getattr(usage, "total_tokens", 0) or 0
    return json.loads(response.choices[0].message.content or "{}"), tokens, model


async def verify(
    question: str,
    decide: Callable[[list[dict]], Awaitable[tuple[dict, int, str]]] = _decide,
    search: Callable[[str, int], Awaitable[list[dict]]] = rag.search,
) -> Outcome:
    """The model selects each next action; every run stops within MAX_STEPS."""
    outcome = Outcome(status="incomplete", answer="I could not verify this against the available policies.")
    evidence: list[dict] = []
    notes: list[dict] = []
    queries: set[str] = set()
    for step in range(1, MAX_STEPS + 1):
        outcome.steps = step
        # Rebuild the prompt from compact notes, never append raw tool transcripts.
        messages = [{"role": "system", "content": SYSTEM},
                    {"role": "user", "content": json.dumps({"question": question,
                     "steps_remaining": MAX_STEPS - step + 1, "notes": notes,
                     "evidence": evidence}, ensure_ascii=False)}]
        try:
            action, tokens, model = await decide(messages)
            outcome.tokens += tokens
            outcome.model = model
        except (llm.AllProvidersFailed, ValueError, TypeError, KeyError) as exc:
            outcome.trajectory.append({"step": step, "action": "model_error", "error": str(exc)})
            outcome.answer = "I cannot verify the policy right now. Please try again later."
            return outcome
        kind = action.get("action") if isinstance(action, dict) else None
        if kind == "search":
            query = action.get("query")
            if not isinstance(query, str) or not query.strip() or len(query) > 300:
                notes.append({"error": "Search requires a nonempty query of at most 300 characters."})
                outcome.trajectory.append({"step": step, "action": "invalid_search"})
                continue
            query = query.strip()
            if query.casefold() in queries:
                notes.append({"error": "That query was already searched. Refine it or clarify."})
                outcome.trajectory.append({"step": step, "action": "duplicate_search", "query": query})
                continue
            queries.add(query.casefold())
            try:
                hits = _compact(await search(query, MAX_HITS))
                evidence = _compact(evidence + hits)
                notes.append({"query": query, "matches": len(hits),
                              "sources": [h["source"] for h in hits]})
                outcome.trajectory.append({"step": step, "action": "search", "query": query,
                                           "matches": len(hits)})
            except Exception as exc:
                notes.append({"query": query, "error": "search unavailable"})
                outcome.trajectory.append({"step": step, "action": "search_error", "query": query,
                                           "error": type(exc).__name__})
        elif kind == "clarify":
            question_to_user = action.get("question")
            if isinstance(question_to_user, str) and question_to_user.strip():
                outcome.status = "needs_clarification"
                outcome.answer = question_to_user.strip()
                outcome.trajectory.append({"step": step, "action": "clarify"})
                return outcome
            notes.append({"error": "Clarification needs a question."})
            outcome.trajectory.append({"step": step, "action": "invalid_clarify"})
        elif kind == "answer":
            answer = action.get("answer")
            citations = action.get("citations")
            if isinstance(answer, str) and answer.strip() and _valid_citations(citations, evidence):
                outcome.status = "completed"
                outcome.answer = answer.strip()
                outcome.citations = citations
                outcome.trajectory.append({"step": step, "action": "answer"})
                return outcome
            notes.append({"error": "Answer rejected: citation quote must occur in visible evidence."})
            outcome.trajectory.append({"step": step, "action": "invalid_answer"})
        else:
            notes.append({"error": "Choose search, clarify, or answer."})
            outcome.trajectory.append({"step": step, "action": "invalid_action"})
    outcome.trajectory.append({"action": "step_limit"})
    return outcome
