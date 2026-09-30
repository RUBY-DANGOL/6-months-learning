import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from io import BytesIO

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import ValidationError
from pypdf import PdfReader

from . import agent, cache, llm, prompts, rag, router, tools
from .config import settings
from .logging_setup import configure
from .ratelimit import enforce
from .schemas import (
    Answer,
    BatchRequest,
    ChatRequest,
    ChatResponse,
    IngestResponse,
    Source,
)

configure()
log = logging.getLogger("assistant.api")

MAX_TOOL_ROUNDS = 3
TOOL_PROBE_TOKENS = 256


@asynccontextmanager
async def lifespan(app: FastAPI):
    router.load()
    try:
        if await rag.collection_size() == 0:
            files, chunks = await rag.index_directory(settings.corpus_dir)
            log.info(
                "indexed bundled corpus",
                extra={"route": "startup", "files": files, "chunks": chunks},
            )
    except Exception as exc:
        log.warning("corpus indexing skipped", extra={"error": str(exc)})
    yield
    await rag.client().close()


app = FastAPI(title="ShopAssist Support Assistant", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.post("/verify", dependencies=[Depends(enforce)])
async def verify_policy(request: ChatRequest) -> dict:
    """Model-directed, bounded cross-source policy verification."""
    return (await agent.verify(request.message)).as_dict()


def response_format() -> dict:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "answer",
            "schema": Answer.model_json_schema(),
            "strict": True,
        },
    }


def build_messages(
    question: str, hits: list[dict], agent: str | None, tool_results: list[dict] | None = None
) -> list[dict]:
    if hits:
        context = "\n\n".join(f"[{h['source']}]\n{h['text']}" for h in hits)
        user = f"{prompts.CONTEXT_HEADER}{context}"
    else:
        user = prompts.NO_CONTEXT
    if tool_results:
        lines = "\n".join(f"[{r['tool']}] {json.dumps(r['result'])}" for r in tool_results)
        user += f"\n\nTool results:\n{lines}"
    user += f"\n\nCustomer message: {question}"
    return [
        {"role": "system", "content": prompts.system(agent)},
        {"role": "user", "content": user},
    ]


async def resolve(request: ChatRequest, route: router.Route) -> tuple[list[dict], str | None, bool | None]:
    if request.use_rag is False or route.gated:
        return [], None, None
    hits = await rag.search(request.message, request.top_k)
    if not hits:
        return [], None, None
    retrieved = hits[0]["category"]
    return hits, retrieved or route.agent, (retrieved == route.agent if retrieved else None)


async def run_tools(question: str, agent: str | None, overrides: dict) -> list[dict]:
    messages = [
        {"role": "system", "content": prompts.system(agent)},
        {"role": "user", "content": question},
    ]
    results: list[dict] = []
    probe = {**overrides, "max_tokens": TOOL_PROBE_TOKENS}
    for _ in range(MAX_TOOL_ROUNDS):
        response, _model = await llm.complete(
            messages, tools=tools.SPECS, tool_choice="auto", **probe
        )
        message = response.choices[0].message
        calls = getattr(message, "tool_calls", None)
        if not calls:
            return results
        messages.append(message.model_dump(exclude_none=True))
        for call in calls:
            try:
                arguments = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                arguments = {}
            result = await tools.dispatch(call.function.name, arguments)
            results.append({"tool": call.function.name, "arguments": arguments, "result": result})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": call.function.name,
                    "content": json.dumps(result)[:4000],
                }
            )
    return results


async def structured_answer(messages: list[dict], overrides: dict) -> tuple[Answer, str]:
    response, model_name = await llm.complete(
        messages, response_format=response_format(), **overrides
    )
    raw = response.choices[0].message.content or "{}"
    try:
        return Answer.model_validate_json(raw), model_name
    except ValidationError:
        pass

    repair = messages + [
        {"role": "assistant", "content": raw},
        {
            "role": "user",
            "content": "That reply was rejected. Return only a JSON object matching this schema: "
            + json.dumps(Answer.model_json_schema()),
        },
    ]
    response, model_name = await llm.complete(
        repair, response_format={"type": "json_object"}, **overrides
    )
    raw = response.choices[0].message.content or "{}"
    try:
        return Answer.model_validate_json(raw), model_name
    except ValidationError:
        return Answer(answer=raw.strip(), confidence="low"), model_name


def degraded_answer(
    hits: list[dict], route: router.Route, agent: str | None, started: float
) -> ChatResponse:
    if hits:
        text = (
            "Our assistant is temporarily unavailable, so here is the relevant policy "
            "wording directly:\n\n"
            + "\n\n".join(f"[{h['source']}] {h['text'][:500]}" for h in hits)
        )
    else:
        text = (
            "Our assistant is temporarily unavailable and no matching policy was found. "
            "Please try again shortly, or ask for a human advisor."
        )
    return ChatResponse(
        answer=text,
        confidence="low",
        agent=agent,
        router_agent=route.agent,
        router_confidence=route.confidence,
        router_energy=route.energy,
        out_of_scope=not hits,
        sources=[Source(**h) for h in hits],
        degraded=True,
        model="none",
        latency_ms=int((time.perf_counter() - started) * 1000),
    )


@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(enforce)])
async def chat(request: ChatRequest) -> ChatResponse:
    started = time.perf_counter()
    temperature = request.temperature if request.temperature is not None else settings.temperature
    top_p = request.top_p if request.top_p is not None else settings.top_p
    overrides = {"temperature": temperature, "top_p": top_p}

    cache_key = cache.key(request.message, temperature, top_p, request.use_tools)
    cached = await cache.get_exact(cache_key)
    kind = "exact"
    if cached is None:
        cached = await cache.get_semantic(request.message)
        kind = "semantic"
    if cached is not None:
        cached["cache"] = kind
        cached["latency_ms"] = int((time.perf_counter() - started) * 1000)
        return ChatResponse(**cached)

    route = router.route(request.message)
    hits, agent, agrees = await resolve(request, route)

    tool_results: list[dict] = []
    try:
        if request.use_tools:
            tool_results = await run_tools(request.message, agent, overrides)
        messages = build_messages(request.message, hits, agent, tool_results)
        answer, model_name = await structured_answer(messages, overrides)
    except llm.AllProvidersFailed as exc:
        log.error("all providers failed", extra={"error": str(exc), "degraded": True})
        return degraded_answer(hits, route, agent, started)

    result = ChatResponse(
        answer=answer.answer,
        confidence=answer.confidence,
        citations=answer.citations,
        follow_up=answer.follow_up,
        agent=agent,
        router_agent=route.agent,
        router_confidence=route.confidence,
        router_energy=route.energy,
        router_agrees=agrees,
        out_of_scope=not hits,
        sources=[Source(**h) for h in hits],
        tool_calls=[r["tool"] for r in tool_results],
        tool_results=tool_results,
        model=model_name,
        latency_ms=int((time.perf_counter() - started) * 1000),
    )
    payload = result.model_dump()
    await cache.set_exact(cache_key, payload)
    await cache.set_semantic(request.message, payload)
    log.info(
        "chat served",
        extra={
            "route": "/chat",
            "agent": agent or "out_of_scope",
            "router_agent": route.agent,
            "router_agrees": agrees,
            "router_confidence": route.confidence,
            "router_energy": route.energy,
            "cache": "miss",
            "model": model_name,
            "latency_ms": result.latency_ms,
        },
    )
    return result


@app.post("/chat/stream", dependencies=[Depends(enforce)])
async def chat_stream(request: ChatRequest):
    route = router.route(request.message)
    hits, agent, agrees = await resolve(request, route)
    messages = build_messages(request.message, hits, agent)
    messages[0]["content"] += "\n- For this reply answer in plain prose, not JSON."
    overrides = {"temperature": request.temperature, "top_p": request.top_p}

    async def events():
        meta = {
            "agent": agent,
            "router_agent": route.agent,
            "router_agrees": agrees,
            "router_confidence": route.confidence,
            "router_energy": route.energy,
            "out_of_scope": not hits,
            "sources": hits,
        }
        yield f"event: meta\ndata: {json.dumps(meta)}\n\n"
        try:
            async for token in llm.stream(messages, **overrides):
                yield f"data: {json.dumps({'token': token})}\n\n"
        except llm.AllProvidersFailed:
            fallback = degraded_answer(hits, route, agent, time.perf_counter())
            yield f"data: {json.dumps({'token': fallback.answer, 'degraded': True})}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/chat/batch", dependencies=[Depends(enforce)])
async def chat_batch(request: BatchRequest) -> list[ChatResponse]:
    started = time.perf_counter()
    results = await asyncio.gather(
        *(chat(ChatRequest(message=m, use_tools=request.use_tools)) for m in request.messages),
        return_exceptions=True,
    )
    empty = router.Route(None, 0.0, 0.0, False, router.load())
    return [
        degraded_answer([], empty, None, started) if isinstance(item, BaseException) else item
        for item in results
    ]


@app.post("/route", dependencies=[Depends(enforce)])
async def route_only(request: BatchRequest) -> list[dict]:
    return [
        {
            "message": message,
            "agent": r.agent,
            "confidence": r.confidence,
            "energy": r.energy,
            "gated": r.gated,
        }
        for message, r in zip(request.messages, router.classify(request.messages))
    ]


@app.post("/ingest", response_model=IngestResponse, dependencies=[Depends(enforce)])
async def ingest(files: list[UploadFile] = File(...)) -> IngestResponse:
    items = []
    for upload in files:
        content = await upload.read()
        name = upload.filename or "upload"
        if name.lower().endswith(".pdf"):
            text = "\n\n".join(p.extract_text() or "" for p in PdfReader(BytesIO(content)).pages)
        else:
            text = content.decode("utf-8", errors="replace")
        items.append((name, text))
    chunks = await rag.index_texts(items)
    return IngestResponse(files=len(items), chunks=chunks, collection=settings.kb_collection)


@app.post("/ingest/corpus", response_model=IngestResponse)
async def ingest_corpus() -> IngestResponse:
    files, chunks = await rag.index_directory(settings.corpus_dir)
    if files == 0:
        raise HTTPException(404, f"no documents found in {settings.corpus_dir}")
    return IngestResponse(files=files, chunks=chunks, collection=settings.kb_collection)


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@app.get("/readyz")
async def readyz() -> dict:
    indexed, redis_up, model_up = await asyncio.gather(
        rag.collection_size(), cache.reachable(), llm.reachable()
    )
    return {
        "ready": bool(redis_up and model_up and router.load()),
        "llm": model_up,
        "redis": redis_up,
        "indexed_chunks": indexed,
        "router": router.load(),
    }


@app.get("/stats")
async def stats() -> dict:
    return {
        "model": settings.llm_model,
        "fallbacks": [t["model"] for t in llm.targets()[1:]],
        "embedding_model": settings.embed_model,
        "indexed_chunks": await rag.collection_size(),
        "router": router.info(),
        "rate_limit_per_min": settings.rate_limit_per_min,
        "max_concurrent_llm": settings.max_concurrent_llm,
        "cache_ttl_seconds": settings.cache_ttl,
        "semantic_threshold": settings.semantic_threshold,
    }
