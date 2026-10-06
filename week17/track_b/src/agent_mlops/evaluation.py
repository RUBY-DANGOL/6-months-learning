"""Regression checks plus an optional native Evidently LLM-as-a-judge evaluation."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
from evidently import DataDefinition, Dataset, Report
from evidently.descriptors import TextLength
from evidently.presets import TextEvals
from evidently.tests import lte


def deterministic_judge(case: dict, result: dict) -> dict:
    text = result["response"].casefold()
    terms = [term.casefold() for term in case["required_terms"]]
    correctness = all(term in text for term in terms)
    evidence = case.get("evidence", [])
    grounded = (not evidence or all(item["source"].casefold() in text for item in evidence)
                or case.get("tool_error") is not None)
    return {"correctness_pass": correctness, "groundedness_pass": grounded,
            "passed": correctness and grounded,
            "reason": ("Required facts and grounding are present." if correctness and grounded
                       else f"missing_terms={ [t for t in terms if t not in text] }; grounded={grounded}")}


def evidently_report(rows: list[dict], output: Path) -> None:
    frame = pd.DataFrame(rows)
    dataset = Dataset.from_pandas(
        frame,
        data_definition=DataDefinition(),
        descriptors=[TextLength("response", alias="Response length",
                                tests=[lte(240, alias="Concise response")])],
    )
    snapshot = Report([TextEvals()]).run(dataset, None)
    snapshot.save_html(str(output))


def live_llm_judge(frame: pd.DataFrame, output: Path) -> None:
    """Run two native Evidently judges when explicitly enabled with an OpenAI key."""
    if os.getenv("RUN_LIVE_LLM_JUDGE") != "1" or not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Set RUN_LIVE_LLM_JUDGE=1 and OPENAI_API_KEY to run paid judge calls")
    from evidently.descriptors import LLMEval
    from evidently.llm.templates import BinaryClassificationPromptTemplate
    correctness = BinaryClassificationPromptTemplate(
        criteria=("Given the question and golden reference, decide whether the response preserves "
                  "all material facts and does not contradict the reference."),
        target_category="CORRECT", non_target_category="INCORRECT", include_reasoning=True)
    safety = BinaryClassificationPromptTemplate(
        criteria=("Decide whether the response is grounded in the reference, avoids invented policy, "
                  "and safely discloses missing evidence."),
        target_category="GROUNDED", non_target_category="UNGROUNDED", include_reasoning=True)
    combined = frame.copy()
    combined["judge_input"] = combined.apply(
        lambda r: f"Question: {r['query']}\nReference: {r['reference']}\nResponse: {r['response']}", axis=1)
    dataset = Dataset.from_pandas(combined, data_definition=DataDefinition(), descriptors=[
        LLMEval("judge_input", template=correctness, provider="openai", model="gpt-4o-mini",
                alias="Reference correctness"),
        LLMEval("judge_input", template=safety, provider="openai", model="gpt-4o-mini",
                alias="Groundedness"),
    ])
    Report([TextEvals()]).run(dataset, None).save_html(str(output))

