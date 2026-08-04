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
    default_price: Decimal = Field(ge=0, max_digits=8, decimal_places=2)


class CatalogItem(BaseModel):
    id: int
    company_id: int
    product_id: int
    price: Decimal = Field(ge=0, max_digits=8, decimal_places=2)


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
    unit_price: Decimal = Field(ge=0, max_digits=8, decimal_places=2)


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
    lead_name: str = Field(alias="lead name")
    company_name: str = Field(alias="company name")
    cuit: str
    email: str
    phone: str
    channel: str
    lead_date: date = Field(alias="lead date")
    status: str
    owner: str

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y", "%b %d, %Y"]

@field_validator("lead_date", mode="before")
@classmethod
def parse_date(cls, v):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(str(v).strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"unrecognised date format: {v}")