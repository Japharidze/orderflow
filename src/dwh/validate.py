'''This module stays minimal as the row validation is done in the schemas.py file
and set level validation is done by dbt tests'''
from pydantic import BaseModel, ValidationError


def split(rows: list[dict], schema: type[BaseModel]) -> tuple[list[dict], list[dict]]:
    '''Just split the rows into good and bad based on the schema validation. 
    The bad rows are returned with the reason for failure.'''

    good, bad = [], []
    for row in rows:
        try:
            good.append(schema(**row).model_dump())
        except ValidationError as e:
            bad.append({"row": str(row), "reason": e.errors()[0]["msg"]})
    return good, bad