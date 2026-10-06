import json

from agent_mlops.agent import VERSIONS, run_case
from agent_mlops.config import CASE_FILE
from agent_mlops.evaluation import deterministic_judge


def test_versions_are_iterative_and_traces_are_complete():
    cases = json.loads(CASE_FILE.read_text(encoding="utf-8"))
    rates = []
    for version in VERSIONS:
        rows = [run_case(case, version) for case in cases]
        rates.append(sum(deterministic_judge(case, row)["passed"]
                         for case, row in zip(cases, rows)))
        for row in rows:
            assert row["termination_reason"]
            assert row["iterations"] == len(row["trace"])
            assert all({"step", "decision", "reason", "tool", "args", "raw_result"}
                       <= set(step) for step in row["trace"])
    assert rates == sorted(rates)
    assert rates[-1] == len(cases)


def test_failure_case_never_invents_deadline_in_best_version():
    case = next(c for c in json.loads(CASE_FILE.read_text(encoding="utf-8"))
                if c["id"] == "tool_failure")
    result = run_case(case, VERSIONS[-1])
    assert "30 days" not in result["response"]
    assert deterministic_judge(case, result)["passed"]

