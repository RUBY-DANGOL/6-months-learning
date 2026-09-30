import time

from fastapi import HTTPException, Request

from .cache import redis_client
from .config import settings


async def enforce(request: Request) -> None:
    if settings.rate_limit_per_min <= 0:
        return
    identity = request.headers.get("x-api-key") or (request.client.host if request.client else "anon")
    window = int(time.time() // 60)
    bucket = f"rate:{identity}:{window}"
    try:
        client = redis_client()
        used = await client.incr(bucket)
        if used == 1:
            await client.expire(bucket, 90)
    except Exception:
        return
    if used > settings.rate_limit_per_min:
        raise HTTPException(
            status_code=429,
            detail=f"rate limit of {settings.rate_limit_per_min} requests/minute exceeded",
            headers={"Retry-After": str(60 - int(time.time() % 60))},
        )
