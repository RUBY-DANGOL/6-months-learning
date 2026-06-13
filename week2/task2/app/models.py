from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customerNumber = Column("customerNumber", Integer, primary_key=True, index=True)
    customerName = Column("customerName", String(50), nullable=False)
    contactLastName = Column("contactLastName", String(50), nullable=False)
    contactFirstName = Column("contactFirstName", String(50), nullable=False)
    phone = Column(String(50), nullable=False)
    addressLine1 = Column("addressLine1", String(50), nullable=False)
    addressLine2 = Column("addressLine2", String(50))
    city = Column(String(50), nullable=False)
    state = Column(String(50))
    postalCode = Column("postalCode", String(15))
    country = Column(String(50), nullable=False)
    salesRepEmployeeNumber = Column("salesRepEmployeeNumber", Integer)
    creditLimit = Column("creditLimit", Numeric(10, 2))

    orders = relationship("Order", back_populates="customer", cascade="all, delete")
    payments = relationship(
        "Payment", back_populates="customer", cascade="all, delete"
    )


class Order(Base):
    __tablename__ = "orders"

    orderNumber = Column("orderNumber", Integer, primary_key=True, index=True)
    orderDate = Column("orderDate", Date, nullable=False)
    requiredDate = Column("requiredDate", Date, nullable=False)
    shippedDate = Column("shippedDate", Date)
    status = Column(String(15), nullable=False)
    comments = Column(Text)
    customerNumber = Column(
        "customerNumber", Integer, ForeignKey("customers.customerNumber"), nullable=False
    )

    customer = relationship("Customer", back_populates="orders")


class Payment(Base):
    __tablename__ = "payments"

    customerNumber = Column(
        "customerNumber",
        Integer,
        ForeignKey("customers.customerNumber"),
        primary_key=True,
    )
    checkNumber = Column("checkNumber", String(50), primary_key=True)
    paymentDate = Column("paymentDate", Date, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)

    customer = relationship("Customer", back_populates="payments")
