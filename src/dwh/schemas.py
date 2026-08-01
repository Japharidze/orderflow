from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator

# --- b2b database ---

class Company(BaseModel):
    id: int
    cuit: str
    user_name: str
    name: str
    is_supplier: bool


class Customer(BaseModel):
    id: int
    company_id: int
    document_number: str
    full_name: str
    date_of_birth: date


class Product(BaseModel):
    id: int
    supplier_id: int
    name: str
    default_price: Decimal = Field(ge=0)


class CatalogItem(BaseModel):
    id: int
    company_id: int
    product_id: int
    price: Decimal = Field(ge=0)


class Order(BaseModel):
    id: int
    company_id: int
    customer_id: int
    ordered_at: datetime


class OrderLine(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)


# --- weblog ---

class WeblogLine(BaseModel):
    ip: str
    ident: str
    username: str
    requested_at: datetime
    request: str
    status: int = Field(ge=100, le=599)
    size: int = Field(ge=0)
    referer: str
    user_agent: str

    @model_validator(mode="before")
    @classmethod
    def not_empty(cls, data: dict) -> dict:
        if not data:
            raise ValueError("malformed line")
        return data

    @field_validator("requested_at", mode="before")
    @classmethod
    def parse_apache_time(cls, v: str) -> datetime:
        return datetime.strptime(v, "%d/%b/%Y:%H:%M:%S %z")

    @field_validator("size", mode="before")
    @classmethod
    def dash_is_zero(cls, v: str) -> str:
        return "0" if v == "-" else v


# --- marketing leads ---

class Lead(BaseModel):
    lead_name: str
    company_name: str
    cuit: str
    email: str
    phone: str
    channel: str
    lead_date: date
    status: str
    owner: str