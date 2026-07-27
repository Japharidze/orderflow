import shutil

from dwh.config import LANDING
from dwh.extract.platform import extract_order_lines
from dwh.load.landing import write_batch
from dwh.validate import OrderLineIn, validate


def run() -> None:
    if LANDING.exists():
        shutil.rmtree(LANDING)

    total_good = total_bad = 0
    for i, batch in enumerate(extract_order_lines()):
        good, bad = validate(batch, OrderLineIn)
        if good:
            write_batch(good, "order_lines", i)
        if bad:
            write_batch(bad, "rejects_order_lines", i)
        total_good += len(good)
        total_bad += len(bad)

    print(f"landed {total_good} rows, rejected {total_bad}")


if __name__ == "__main__":
    run()