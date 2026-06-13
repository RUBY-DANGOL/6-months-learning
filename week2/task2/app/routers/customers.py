import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/", response_model=List[schemas.CustomerOut])
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    logger.info("GET /customers?skip=%s&limit=%s", skip, limit)
    return crud.get_customers(db, skip=skip, limit=limit)


@router.get("/{customer_number}", response_model=schemas.CustomerOut)
def read_customer(customer_number: int, db: Session = Depends(get_db)):
    logger.info("GET /customers/%s", customer_number)
    customer = crud.get_customer(db, customer_number)
    if not customer:
        logger.warning("Customer customerNumber=%s not found", customer_number)
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("/", response_model=schemas.CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer: schemas.CustomerCreate, db: Session = Depends(get_db)
):
    logger.info("POST /customers")
    return crud.create_customer(db, customer)


@router.put("/{customer_number}", response_model=schemas.CustomerOut)
def update_customer(
    customer_number: int, customer: schemas.CustomerUpdate, db: Session = Depends(get_db)
):
    logger.info("PUT /customers/%s", customer_number)
    updated = crud.update_customer(db, customer_number, customer)
    if not updated:
        logger.warning("Customer customerNumber=%s not found", customer_number)
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated


@router.delete("/{customer_number}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_number: int, db: Session = Depends(get_db)):
    logger.info("DELETE /customers/%s", customer_number)
    deleted = crud.delete_customer(db, customer_number)
    if not deleted:
        logger.warning("Customer customerNumber=%s not found", customer_number)
        raise HTTPException(status_code=404, detail="Customer not found")
    return None


@router.get("/{customer_number}/orders", response_model=List[schemas.OrderOut])
def read_customer_orders(customer_number: int, db: Session = Depends(get_db)):
    logger.info("GET /customers/%s/orders", customer_number)
    customer = crud.get_customer(db, customer_number)
    if not customer:
        logger.warning("Customer customerNumber=%s not found", customer_number)
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer.orders


@router.get("/{customer_number}/payments", response_model=List[schemas.PaymentOut])
def read_customer_payments(customer_number: int, db: Session = Depends(get_db)):
    logger.info("GET /customers/%s/payments", customer_number)
    customer = crud.get_customer(db, customer_number)
    if not customer:
        logger.warning("Customer customerNumber=%s not found", customer_number)
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer.payments
