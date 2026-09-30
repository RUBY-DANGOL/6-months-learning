import asyncio
import logging
import time
from collections.abc import AsyncIterator

import httpx
import litellm

from .config import settings

litellm.drop_params = True
litellm.suppress_debug_info = True
litellm.set_verbose = False

log = logging.getLogger("assistant.llm")
_gate = asyncio.Semaphore(settings.max_concurrent_llm)
_open_until: dict[str, float] = {}
_failures: dict[str, int] = {}


class AllProvidersFailed(Exception):
    pass


def targets() -> list[dict]:
    chain = [
        {
            "model": f"openai/{settings.llm_model}",
            "api_base": settings.llm_base_url,
            "api_key": settings.llm_api_key,
        }
    ]
    for name in (m.strip() for m in settings.fallback_models.split(",")):
        if name:
            chain.append({"model": name})
    return chain


def _tripped(model: str) -> bool:
    return time.monotonic() < _open_until.get(model, 0.0)


def _record_success(model: str) -> None:
    _failures.pop(model, None)
    _open_until.pop(model, None)


def _record_failure(model: str) -> None:
    _failures[model] = _failures.get(model, 0) + 1
    if _failures[model] >= settings.breaker_threshold:
        _open_until[model] = time.monotonic() + settings.breaker_cooldown
        log.warning(
            "circuit opened", extra={"target": model, "error": f"{_failures[model]} consecutive failures"}
        )


def _params(overrides: dict | None) -> dict:
    base = {
        "temperature": settings.temperature,
        "top_p": settings.top_p,
        "max_tokens": settings.max_tokens,
        "timeout": settings.request_timeout,
        "num_retries": settings.num_retries,
    }
    base.update({k: v for k, v in (overrides or {}).items() if v is not None})
    return base


async def complete(messages: list[dict], **kwargs):
    errors = []
    async with _gate:
        for target in targets():
            model = target["model"]
            if _tripped(model):
                errors.append(f"{model}: circuit open")
                continue
            try:
                response = await litellm.acompletion(
                    messages=messages, **target, **_params(kwargs)
                )
                _record_success(model)
                return response, model
            except Exception as exc:
                _record_failure(model)
                errors.append(f"{model}: {exc}")
                log.warning("provider failed", extra={"target": model, "error": str(exc)})
    raise AllProvidersFailed(" | ".join(errors) or "no providers available")


async def stream(messages: list[dict], **kwargs) -> AsyncIterator[str]:
    errors = []
    async with _gate:
        for target in targets():
            model = target["model"]
            if _tripped(model):
                errors.append(f"{model}: circuit open")
                continue
            try:
                chunks = await litellm.acompletion(
                    messages=messages, stream=True, **target, **_params(kwargs)
                )
                _record_success(model)
                async for part in chunks:
                    token = part.choices[0].delta.content
                    if token:
                        yield token
                return
            except Exception as exc:
                _record_failure(model)
                errors.append(f"{model}: {exc}")
    raise AllProvidersFailed(" | ".join(errors) or "no providers available")


async def reachable() -> bool:
    url = settings.llm_base_url.rstrip("/") + "/models"
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(
                url, headers={"Authorization": f"Bearer {settings.llm_api_key}"}
            )
        return response.status_code < 500
    except Exception:
        return False
