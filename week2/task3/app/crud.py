import logging
from typing import Any

from app.core.database import get_pool

logger = logging.getLogger(__name__)


async def _count_table(table: str) -> int:
    query = f'SELECT COUNT(*) FROM "{table}"'
    logger.info("db count start", extra={"table": table})
    try:
        pool = get_pool()
        result: Any = await pool.fetchval(query)
        count = int(result or 0)
        logger.info("db count complete", extra={"table": table, "count": count})
        return count
    except Exception:
        logger.exception("db count failed", extra={"table": table})
        raise


async def get_customers_count() -> int:
    return await _count_table("customers")


async def get_orders_count() -> int:
    return await _count_table("orders")


async def get_products_count() -> int:
    return await _count_table("products")


async def get_employees_count() -> int:
    return await _count_table("employees")


async def get_offices_count() -> int:
    return await _count_table("offices")


async def get_payments_count() -> int:
    return await _count_table("payments")


async def get_orderdetails_count() -> int:
    return await _count_table("orderdetails")


async def get_productlines_count() -> int:
    return await _count_table("productlines")
