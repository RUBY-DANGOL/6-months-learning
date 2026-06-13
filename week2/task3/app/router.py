import asyncio
import logging
import time
from typing import Dict

from fastapi import APIRouter, HTTPException, Request

from app import crud

logger = logging.getLogger(__name__)

router = APIRouter()


def _log_success(path: str, status: int) -> None:
    logger.info("request complete", extra={"path": path, "status": status})


def _log_failure(path: str, status: int) -> None:
    logger.error("request failed", extra={"path": path, "status": status})


@router.get("/customers/count")
async def customers_count(request: Request) -> Dict[str, int]:
    logger.info("request start", extra={"path": request.url.path})
    try:
        count = await crud.get_customers_count()
        _log_success(request.url.path, 200)
        return {"customers": count}
    except Exception as exc:
        _log_failure(request.url.path, 500)
        raise HTTPException(status_code=500, detail="failed to fetch customers count") from exc


@router.get("/orders/count")
async def orders_count(request: Request) -> Dict[str, int]:
    logger.info("request start", extra={"path": request.url.path})
    try:
        count = await crud.get_orders_count()
        _log_success(request.url.path, 200)
        return {"orders": count}
    except Exception as exc:
        _log_failure(request.url.path, 500)
        raise HTTPException(status_code=500, detail="failed to fetch orders count") from exc


@router.get("/products/count")
async def products_count(request: Request) -> Dict[str, int]:
    logger.info("request start", extra={"path": request.url.path})
    try:
        count = await crud.get_products_count()
        _log_success(request.url.path, 200)
        return {"products": count}
    except Exception as exc:
        _log_failure(request.url.path, 500)
        raise HTTPException(status_code=500, detail="failed to fetch products count") from exc


@router.get("/employees/count")
async def employees_count(request: Request) -> Dict[str, int]:
    logger.info("request start", extra={"path": request.url.path})
    try:
        count = await crud.get_employees_count()
        _log_success(request.url.path, 200)
        return {"employees": count}
    except Exception as exc:
        _log_failure(request.url.path, 500)
        raise HTTPException(status_code=500, detail="failed to fetch employees count") from exc


@router.get("/offices/count")
async def offices_count(request: Request) -> Dict[str, int]:
    logger.info("request start", extra={"path": request.url.path})
    try:
        count = await crud.get_offices_count()
        _log_success(request.url.path, 200)
        return {"offices": count}
    except Exception as exc:
        _log_failure(request.url.path, 500)
        raise HTTPException(status_code=500, detail="failed to fetch offices count") from exc


@router.get("/payments/count")
async def payments_count(request: Request) -> Dict[str, int]:
    logger.info("request start", extra={"path": request.url.path})
    try:
        count = await crud.get_payments_count()
        _log_success(request.url.path, 200)
        return {"payments": count}
    except Exception as exc:
        _log_failure(request.url.path, 500)
        raise HTTPException(status_code=500, detail="failed to fetch payments count") from exc


@router.get("/orderdetails/count")
async def orderdetails_count(request: Request) -> Dict[str, int]:
    logger.info("request start", extra={"path": request.url.path})
    try:
        count = await crud.get_orderdetails_count()
        _log_success(request.url.path, 200)
        return {"orderdetails": count}
    except Exception as exc:
        _log_failure(request.url.path, 500)
        raise HTTPException(status_code=500, detail="failed to fetch orderdetails count") from exc


@router.get("/productlines/count")
async def productlines_count(request: Request) -> Dict[str, int]:
    logger.info("request start", extra={"path": request.url.path})
    try:
        count = await crud.get_productlines_count()
        _log_success(request.url.path, 200)
        return {"productlines": count}
    except Exception as exc:
        _log_failure(request.url.path, 500)
        raise HTTPException(status_code=500, detail="failed to fetch productlines count") from exc


@router.get("/overall_counts")
async def overall_counts(request: Request) -> Dict[str, int]:
    logger.info("request start", extra={"path": request.url.path})
    start = time.perf_counter()
    try:
        tasks = [
            crud.get_customers_count(),
            crud.get_orders_count(),
            crud.get_products_count(),
            crud.get_employees_count(),
            crud.get_offices_count(),
            crud.get_payments_count(),
            crud.get_orderdetails_count(),
            crud.get_productlines_count(),
        ]
        logger.info("concurrency start", extra={"task_count": len(tasks)})
        (
            customers,
            orders,
            products,
            employees,
            offices,
            payments,
            orderdetails,
            productlines,
        ) = await asyncio.gather(*tasks)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("concurrency complete", extra={"elapsed_ms": round(elapsed_ms, 2)})
        _log_success(request.url.path, 200)
        return {
            "customers": customers,
            "orders": orders,
            "products": products,
            "employees": employees,
            "offices": offices,
            "payments": payments,
            "orderdetails": orderdetails,
            "productlines": productlines,
        }
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.error("concurrency failed", extra={"elapsed_ms": round(elapsed_ms, 2)})
        _log_failure(request.url.path, 500)
        raise HTTPException(status_code=500, detail="failed to fetch overall counts") from exc
