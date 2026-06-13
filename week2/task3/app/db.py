import logging
from typing import Optional

import asyncpg

logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None


async def init_pool(database_url: str) -> None:
    global _pool
    if _pool is not None:
        return
    logger.info("db pool init start")
    _pool = await asyncpg.create_pool(dsn=database_url, min_size=1, max_size=10)
    logger.info("db pool init complete")


async def close_pool() -> None:
    global _pool
    if _pool is None:
        return
    logger.info("db pool close start")
    await _pool.close()
    _pool = None
    logger.info("db pool close complete")


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("database pool is not initialized")
    return _pool
