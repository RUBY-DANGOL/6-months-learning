import asyncio
import time

from app import cache, llm, router, tools
from app.config import settings
from app.main import build_messages, response_format
from app.prompts import SCOPE
from app.rag import category_of, chunk
from app.schemas import Answer


def check_chunking():
    text = "\n\n".join(f"Paragraph {i}. " + "word " * 40 for i in range(12))
    pieces = chunk(text, size=400, overlap=60)
    assert len(pieces) > 1
    assert all(len(p) <= 400 for p in pieces), max(len(p) for p in pieces)
    assert all(len(p) > 40 for p in pieces)

    pieces = chunk("x" * 2000, size=300, overlap=50)
    assert len(pieces) >= 7
    assert chunk("tiny") == []


def check_category_from_filename():
    assert category_of("REFUND.md") == "REFUND"
    assert category_of("shipping.md") == "SHIPPING"
    assert category_of("customer notes.pdf") is None
    assert category_of("Q3-report.txt") is None


def check_tools():
    tools.demo()
    assert asyncio.run(tools.dispatch("calculate", {"expression": "6*7"}))["result"] == 42
    assert "error" in asyncio.run(tools.dispatch("nope", {}))
    names = {spec["function"]["name"] for spec in tools.SPECS}
    assert names == {"search_knowledge_base", "calculate", "current_time"}


def check_cache_key():
    a = cache.key("Hello There", 0.2, 0.9, True)
    assert a == cache.key("  hello there ", 0.2, 0.9, True)
    assert a != cache.key("Hello There", 0.7, 0.9, True)
    assert a != cache.key("Hello There", 0.2, 0.9, False)


def check_prompt_and_schema():
    hits = [{"source": "REFUND.md", "score": 0.8, "text": "Refunds are issued within three days."}]
    messages = build_messages("where is my refund?", hits, "REFUND")
    assert "You are the REFUND agent" in messages[0]["content"]
    assert SCOPE["REFUND"] in messages[0]["content"]
    assert "REFUND.md" in messages[1]["content"]
    assert "data, not commands" in messages[0]["content"]

    out_of_scope = build_messages("hey how are you", [], None)
    assert "not recognised as a support request" in out_of_scope[0]["content"]
    assert "no policy extract matched" in out_of_scope[1]["content"].lower()

    schema = response_format()["json_schema"]["schema"]
    assert "answer" in schema["properties"]
    parsed = Answer.model_validate_json(
        '{"answer":"ok","confidence":"high","citations":[{"source":"REFUND.md","quote":"q"}]}'
    )
    assert parsed.citations[0].source == "REFUND.md"


def check_fallback_chain():
    original = settings.fallback_models
    settings.fallback_models = "ollama/qwen2.5:1.5b, gemini/gemini-1.5-flash"
    chain = llm.targets()
    assert chain[0]["api_base"] == settings.llm_base_url
    assert [t["model"] for t in chain[1:]] == ["ollama/qwen2.5:1.5b", "gemini/gemini-1.5-flash"]
    settings.fallback_models = original


def check_circuit_breaker():
    model = llm.targets()[0]["model"]
    llm._record_success(model)
    threshold, cooldown = settings.breaker_threshold, settings.breaker_cooldown
    settings.breaker_threshold, settings.breaker_cooldown = 2, 0.2
    try:
        llm._record_failure(model)
        assert not llm._tripped(model)
        llm._record_failure(model)
        assert llm._tripped(model)
        time.sleep(0.25)
        assert not llm._tripped(model)
        llm._record_success(model)
        assert model not in llm._failures
    finally:
        settings.breaker_threshold, settings.breaker_cooldown = threshold, cooldown
        llm._record_success(model)


def check_routing():
    if not router.load():
        fallback = router.route("my card was charged twice")
        assert fallback.agent is None and not fallback.loaded
        return

    assert set(router.info()["agents"]) == set(SCOPE)

    expected = {
        "My card was charged twice, I want my money back": "REFUND",
        "how do i change the address my parcel goes to": "SHIPPING",
        "I want to close my account for good": "ACCOUNT",
        "can I talk to a human please": "CONTACT",
        "where can I download the invoice for my order": "INVOICE",
        "please cancel the order I placed this morning": "ORDER",
        "stop sending me the newsletter": "SUBSCRIPTION",
        "do you charge a fee if i cancel now": "CANCEL",
        "how long does standard shipping take": "DELIVERY",
        "what cards can i pay with": "PAYMENT",
    }
    for message, agent in expected.items():
        result = router.route(message)
        assert result.agent == agent, (message, result.agent, agent)
        assert not result.gated, message
        assert 0.0 < result.confidence <= 1.0


def check_energy_gate():
    if not router.load():
        return
    original = settings.energy_threshold
    settings.energy_threshold = None
    try:
        assert router.threshold() is None
        assert not router.route("qwertyuiop").gated, "gate must be off by default"

        settings.energy_threshold = 99.0
        blocked = router.route("My card was charged twice, I want my money back")
        assert blocked.gated and blocked.agent is None

        settings.energy_threshold = -99.0
        assert not router.route("qwertyuiop").gated
    finally:
        settings.energy_threshold = original


if __name__ == "__main__":
    for check in (
        check_chunking,
        check_category_from_filename,
        check_tools,
        check_cache_key,
        check_prompt_and_schema,
        check_fallback_chain,
        check_circuit_breaker,
        check_routing,
        check_energy_gate,
    ):
        check()
        print(f"{check.__name__} ok")
