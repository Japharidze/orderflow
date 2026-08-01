from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from dwh.config import PG_URL


class Base(DeclarativeBase):
    pass


class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True)
    cuit: Mapped[str] = mapped_column(String(13), unique=True)
    user_name: Mapped[str] = mapped_column(String(20), unique=True) # for weblog matching %u
    name: Mapped[str]
    is_supplier: Mapped[bool] = mapped_column(default=False)


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    document_number: Mapped[str] = mapped_column(String(20), unique=True)
    full_name: Mapped[str]
    date_of_birth: Mapped[date]


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    name: Mapped[str]
    default_price: Mapped[Decimal]


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    ordered_at: Mapped[datetime]


class OrderLine(Base):
    __tablename__ = "order_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    unit_price: Mapped[Decimal]

class CatalogItem(Base):
    __tablename__ = "catalogs"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    price: Mapped[Decimal]

def engine():
    return create_engine(PG_URL)