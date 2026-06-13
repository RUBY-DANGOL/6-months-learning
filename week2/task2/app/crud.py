import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from app import models, schemas

logger = logging.getLogger(__name__)


def get_customer(db: Session, customer_number: int) -> Optional[models.Customer]:
    logger.info("Fetching customer customerNumber=%s", customer_number)
    return (
        db.query(models.Customer)
        .filter(models.Customer.customerNumber == customer_number)
        .first()
    )


def get_customers(db: Session, skip: int = 0, limit: int = 10) -> List[models.Customer]:
    logger.info("Listing customers skip=%s limit=%s", skip, limit)
    return db.query(models.Customer).offset(skip).limit(limit).all()


def create_customer(db: Session, customer: schemas.CustomerCreate) -> models.Customer:
    logger.info("Creating customer customerNumber=%s", customer.customerNumber)
    db_customer = models.Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def update_customer(
    db: Session, customer_number: int, customer: schemas.CustomerUpdate
) -> Optional[models.Customer]:
    logger.info("Updating customer customerNumber=%s", customer_number)
    db_customer = get_customer(db, customer_number)
    if not db_customer:
        logger.warning("Customer customerNumber=%s not found for update", customer_number)
        return None

    update_data = customer.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_customer, key, value)

    db.commit()
    db.refresh(db_customer)
    return db_customer


def delete_customer(db: Session, customer_number: int) -> bool:
    logger.info("Deleting customer customerNumber=%s", customer_number)
    db_customer = get_customer(db, customer_number)
    if not db_customer:
        logger.warning("Customer customerNumber=%s not found for delete", customer_number)
        return False

    db.delete(db_customer)
    db.commit()
    return True


def get_customer_orders(db: Session, customer_number: int):
    logger.info("Fetching orders for customer customerNumber=%s", customer_number)
    return (
        db.query(models.Order)
        .filter(models.Order.customerNumber == customer_number)
        .all()
    )


def get_customer_payments(db: Session, customer_number: int):
    logger.info("Fetching payments for customer customerNumber=%s", customer_number)
    return (
        db.query(models.Payment)
        .filter(models.Payment.customerNumber == customer_number)
        .all()
    )
