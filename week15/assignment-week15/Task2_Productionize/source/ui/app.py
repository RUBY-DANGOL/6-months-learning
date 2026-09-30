import json
import os

import httpx
import streamlit as st

API = os.getenv("API_URL", "http://api:8080")

st.set_page_config(page_title="ShopAssist Support", layout="wide")


@st.cache_data(ttl=10, show_spinner=False)
def get_json(path: str, timeout: float = 5.0):
    try:
        return httpx.get(f"{API}{path}", timeout=timeout).json()
    except Exception as exc:
        return {"error": str(exc)}


def stream_answer(payload: dict):
    meta = {}
    with httpx.stream("POST", f"{API}/chat/stream", json=payload, timeout=180) as response:
        response.raise_for_status()
        event = None
        for line in response.iter_lines():
            if line.startswith("event: "):
                event = line[7:].strip()
            elif line.startswith("data: "):
                data = json.loads(line[6:])
                if event == "meta":
                    meta = data
                    event = None
                elif "token" in data:
                    yield data["token"]
    st.session_state.last_meta = meta


with st.sidebar:
    st.subheader("Backend")
    status = get_json("/readyz")
    if status.get("ready"):
        st.success("ready")
    else:
        st.warning("degraded")
    st.json(status, expanded=False)

    st.subheader("Generation")
    temperature = st.slider("temperature", 0.0, 1.5, 0.2, 0.05)
    top_p = st.slider("top_p", 0.1, 1.0, 0.9, 0.05)
    top_k = st.slider("policy extracts", 1, 10, 4)
    use_tools = st.checkbox("function calling", value=True)
    use_rag = st.selectbox("retrieval", ["on", "off"])
    streaming = st.checkbox("stream tokens", value=False)

    st.subheader("Policy documents")
    uploads = st.file_uploader(
        "add documents", type=["pdf", "md", "txt"], accept_multiple_files=True
    )
    if uploads and st.button("Index uploads"):
        files = [("files", (f.name, f.getvalue())) for f in uploads]
        result = httpx.post(f"{API}/ingest", files=files, timeout=300).json()
        st.success(f"{result['chunks']} chunks from {result['files']} file(s)")
    if st.button("Reindex policies"):
        result = httpx.post(f"{API}/ingest/corpus", timeout=300).json()
        st.success(f"{result.get('chunks', 0)} chunks indexed")

st.title("ShopAssist Support Assistant")

if "history" not in st.session_state:
    st.session_state.history = []

for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])
        if turn.get("meta"):
            st.caption(turn["meta"])

question = st.chat_input("Describe your problem, for example: my card was charged twice")
if question:
    st.session_state.history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    payload = {
        "message": question,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "use_tools": use_tools,
        "use_rag": use_rag == "on",
    }

    with st.chat_message("assistant"):
        if streaming:
            text = st.write_stream(stream_answer(payload))
            meta = st.session_state.get("last_meta", {})
            caption = f"agent: {meta.get('agent') or 'out of scope'} · streamed"
            sources = meta.get("sources", [])
        else:
            try:
                data = httpx.post(f"{API}/chat", json=payload, timeout=180).json()
            except Exception as exc:
                st.error(f"request failed: {exc}")
                st.stop()
            if "detail" in data:
                st.error(data["detail"])
                st.stop()
            text = data["answer"]
            st.markdown(text)
            sources = data["sources"]
            caption = (
                f"agent: {data['agent'] or 'out of scope'} · confidence: {data['confidence']} · "
                f"cache: {data['cache']} · model: {data['model']} · {data['latency_ms']} ms"
            )
            if data["tool_calls"]:
                caption += " · tools: " + ", ".join(data["tool_calls"])
            if data["router_agent"]:
                agrees = data["router_agrees"]
                verdict = "agrees" if agrees else "disagrees" if agrees is False else "unchecked"
                st.caption(
                    f"router: {data['router_agent']} at {data['router_confidence']:.3f} "
                    f"(energy {data['router_energy']:.2f}) — retrieval {verdict}"
                )
            if data["out_of_scope"]:
                st.info("No policy matched this message, so it was answered without one.")
            if data["degraded"]:
                st.warning("served in degraded mode, the language model did not respond")

        st.caption(caption)
        if not streaming and data.get("tool_results"):
            with st.expander(f"{len(data['tool_results'])} tool call(s)"):
                for call in data["tool_results"]:
                    st.code(f"{call['tool']}({json.dumps(call['arguments'])}) -> {json.dumps(call['result'])}")
        if sources:
            with st.expander(f"{len(sources)} retrieved passages"):
                for hit in sources:
                    st.markdown(f"**{hit['source']}** · {hit.get('category') or 'uncategorised'} · score {hit['score']}")
                    st.text(hit["text"][:800])

    st.session_state.history.append({"role": "assistant", "content": text, "meta": caption})
