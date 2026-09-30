"""Local Streamlit demonstration of the real Week 16 decision loop."""

import asyncio
import importlib.util
import json
from pathlib import Path

import streamlit as st

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "evaluate_agent.py"
spec = importlib.util.spec_from_file_location("evaluate_agent", SCRIPT)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
agent = harness.load_agent()

st.set_page_config(page_title="ShopAssist Agent Demo", layout="wide")
st.title("ShopAssist · Policy verification")
st.caption("Local demonstration using the real agent loop and scripted model/search fixtures. "
           "No Docker, Ollama, or API key is required.")

examples = {case["name"]: case for case in harness.CASES}
labels = {
    "refine_search": "Search again after an empty result",
    "clarification": "Ask the customer to clarify",
    "invented_citation": "Reject an invented policy quote",
    "injected_tool_failure": "Handle a search timeout",
    "step_limit": "Stop after five decisions",
}
selected = st.selectbox("Choose a scenario", list(examples),
                        format_func=lambda name: labels[name])
case = examples[selected]
st.info(f"Customer: {case['question']}")


async def demonstrate(item):
    decisions = iter(item["decisions"])
    decisions_seen = []

    async def decide(messages):
        context = json.loads(messages[1]["content"])
        action = next(decisions)
        decisions_seen.append({"step": len(decisions_seen) + 1,
                               "visible_sources": [h["source"] for h in context["evidence"]],
                               "model_decision": action})
        return action, 42, "scripted-model"

    async def search(query, top_k):
        if query == item.get("fail_query"):
            raise TimeoutError("injected search timeout")
        return item["hits"].get(query, [])[:top_k]

    result = await agent.verify(item["question"], decide=decide, search=search)
    return result, decisions_seen


if st.button("Run agent", type="primary"):
    result, decisions_seen = asyncio.run(demonstrate(case))
    st.session_state.demo_result = (selected, result.as_dict(), decisions_seen)

if "demo_result" in st.session_state:
    name, result, decisions_seen = st.session_state.demo_result
    if name == selected:
        st.subheader("Result")
        st.write(result["answer"])
        a, b, c = st.columns(3)
        a.metric("Status", result["status"])
        b.metric("Decisions", result["steps"])
        c.metric("Simulated tokens", result["tokens"])

        st.subheader("Decision trajectory")
        for index, decision in enumerate(decisions_seen):
            event = result["trajectory"][index]
            with st.expander(f"Step {decision['step']}: {event['action']}", expanded=True):
                st.write("Evidence visible before decision:",
                         ", ".join(decision["visible_sources"]) or "none")
                st.json(decision["model_decision"])
                st.write("Agent event:")
                st.json(event)
        if len(result["trajectory"]) > len(decisions_seen):
            st.warning("Stopped at the five-decision limit.")
        if result["citations"]:
            st.subheader("Validated citations")
            st.json(result["citations"])
