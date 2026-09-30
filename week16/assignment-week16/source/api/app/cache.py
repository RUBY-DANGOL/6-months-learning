import hashlib
import json

import redis.asyncio as aioredis

from . import rag
from .config import settings

_redis: aioredis.Redis | None = None


def semantic_collection() -> str:
    return f"{settings.cache_collection}_{hashlib.sha1(settings.llm_model.encode()).hexdigest()[:8]}"


def redis_client() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
    return _redis


def key(message: str, temperature: float, top_p: float, use_tools: bool) -> str:
    raw = json.dumps([settings.llm_model, message.strip().lower(), temperature, top_p, use_tools])
    return "chat:" + hashlib.sha256(raw.encode()).hexdigest()


async def get_exact(cache_key: str) -> dict | None:
    try:
        hit = await redis_client().get(cache_key)
    except Exception:
        return None
    return json.loads(hit) if hit else None


async def set_exact(cache_key: str, payload: dict) -> None:
    try:
        await redis_client().setex(cache_key, settings.cache_ttl, json.dumps(payload))
    except Exception:
        pass


async def get_semantic(message: str) -> dict | None:
    try:
        hits = await rag.client().query(
            collection_name=semantic_collection(), query_text=message, limit=1
        )
    except Exception:
        return None
    if hits and hits[0].score >= settings.semantic_threshold:
        return json.loads(hits[0].metadata["payload"])
    return None


async def set_semantic(message: str, payload: dict) -> None:
    try:
        await rag.client().add(
            collection_name=semantic_collection(),
            documents=[message],
            metadata=[{"payload": json.dumps(payload)}],
            ids=[int(hashlib.sha1(message.strip().lower().encode()).hexdigest()[:15], 16)],
        )
    except Exception:
        pass


async def reachable() -> bool:
    try:
        return await redis_client().ping()
    except Exception:
        return False
