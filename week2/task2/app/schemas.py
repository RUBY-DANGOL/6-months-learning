import logging
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class OrderOut(BaseModel):
    orderNumber: int
    orderDate: date
    requiredDate: date
    shippedDate: Optional[date] = None
    status: str
    comments: Optional[str] = None
    customerNumber: int

    class Config:
        from_attributes = True


class PaymentOut(BaseModel):
    customerNumber: int
    checkNumber: str
    paymentDate: date
    amount: float

    class Config:
        from_attributes = True


class CustomerCreate(BaseModel):
    customerNumber: int
    customerName: str = Field(..., min_length=1, max_length=50)
    contactLastName: str = Field(..., min_length=1, max_length=50)
    contactFirstName: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=1, max_length=50)
    addressLine1: str = Field(..., min_length=1, max_length=50)
    addressLine2: Optional[str] = Field(None, max_length=50)
    city: str = Field(..., min_length=1, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    postalCode: Optional[str] = Field(None, max_length=15)
    country: str = Field(..., min_length=1, max_length=50)
    salesRepEmployeeNumber: Optional[int] = None
    creditLimit: Optional[float] = None


class CustomerUpdate(BaseModel):
    customerName: Optional[str] = Field(None, min_length=1, max_length=50)
    contactLastName: Optional[str] = Field(None, min_length=1, max_length=50)
    contactFirstName: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, min_length=1, max_length=50)
    addressLine1: Optional[str] = Field(None, min_length=1, max_length=50)
    addressLine2: Optional[str] = Field(None, max_length=50)
    city: Optional[str] = Field(None, min_length=1, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    postalCode: Optional[str] = Field(None, max_length=15)
    country: Optional[str] = Field(None, min_length=1, max_length=50)
    salesRepEmployeeNumber: Optional[int] = None
    creditLimit: Optional[float] = None


class CustomerOut(BaseModel):
    customerNumber: int
    customerName: str
    contactLastName: str
    contactFirstName: str
    phone: str
    addressLine1: str
    addressLine2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: str
    salesRepEmployeeNumber: Optional[int] = None
    creditLimit: Optional[float] = None
    orders: List[OrderOut] = Field(default_factory=list)
    payments: List[PaymentOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


def log_validation_error(exc: ValidationError) -> None:
    logger.warning("Schema validation error: %s", exc)
