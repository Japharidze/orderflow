from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ValidationError


class OrderLineIn(BaseModel):
    id: int
    order_id: int
    company_id: int
    customer_id: int
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    ordered_at: datetime


def validate(rows: list[dict], model: type[BaseModel]) -> tuple[list[dict], list[dict]]:
    """Split a batch into (valid rows, rejected rows with a reason)."""
    good, bad = [], []
    for row in rows:
        try:
            good.append(model(**row).model_dump())
        except ValidationError as e:
            bad.append({"row": str(row), "reason": str(e.errors()[0]["msg"])})
    return good, bad