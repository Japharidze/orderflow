import shutil

from dwh import schemas
from dwh.config import LANDING
from dwh.db import models
from dwh.extract import leads, table, weblog
from dwh.load.landing import write_batch
from dwh.validate import split

DB_MODELS = [
    models.CatalogItem, models.Company, models.Customer,
    models.Product, models.Order, models.OrderLine]
DB_SCHEMAS = [
    schemas.CatalogItem, schemas.Company, schemas.Customer,
    schemas.Product, schemas.Order, schemas.OrderLine]
MODEL_NAMES = [obj.__tablename__.lower() for obj in DB_MODELS]

DB_ITERATOR_TUPLES = [(table(model), schema) for model, schema in zip(DB_MODELS, DB_SCHEMAS)]
ITERATORS = {name : tup for name, tup in zip(MODEL_NAMES, DB_ITERATOR_TUPLES)}
ITERATORS = ITERATORS | {
    "weblog": (weblog(), schemas.WeblogLine),
    "leads": (leads(), schemas.Lead),
}

def run() -> None:
    if LANDING.exists():
        shutil.rmtree(LANDING)

    total_good = total_bad = 0
    for name, (iterator, schema) in ITERATORS.items():
        for i, batch in enumerate(iterator):
            good, bad = split(batch, schema)
            if good:
                write_batch(good, f"{name}", i)
            if bad:
                write_batch(bad, f"rejects_{name}", i)
            total_good += len(good)
            total_bad += len(bad)

    print(f"landed {total_good} rows, rejected {total_bad}")


if __name__ == "__main__":
    run()