import random
import argparse
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker
from sqlalchemy import select
from sqlalchemy.orm import Session

from dwh.db.models import Company, engine
from dwh.config import LEADS_FILE

parser = argparse.ArgumentParser()
parser.add_argument('--rows', type=int, help="Number")
fake = Faker("es_AR")
Faker.seed(42)
random.seed(42)


N_LEADS = 300
YEAR_SECONDS = int(3.154e7)

CHANNELS = (["ads", "referral", "event", "cold outreach", "webinar"],
            [35, 25, 15, 20, 5])
STATUSES = (["new", "contacted", "qualified", "converted", "lost"],
            [30, 25, 20, 10, 15])

# how the same date can look when different people fill the same sheet
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y", "%b %d, %Y"]

OWNERS = ["m.silva", "j.pereira", "a.gomez", "l.ferreira"]


def _messy_case(text: str) -> str:
    # marketing people type however they feel that day
    return random.choice([text, text.upper(), text.lower(), text.title()])


def _messy_spaces(text: str) -> str:
    return random.choice([text, f" {text}", f"{text}  ", f" {text} "])


def _broken_cuit(cuit: str) -> str:
    # same number, wrong checksum, or just not a cuit at all
    digits = cuit.replace("-", "")
    return random.choice([
        f"{digits[:2]}-{digits[2:10]}-{random.randint(0, 9)}",  # bad check digit
        digits[:-1],                                            # too short
        "",                                                     # nobody filled it
        "n/a",
    ])


def _generate_row(cuits: list[str]) -> dict:
    # most leads are companies we already know, some are new names
    known = random.random() < 0.6
    cuit = random.choice(cuits) if known else fake.numerify("3#-########-#")

    if random.random() < 0.12:
        cuit = _broken_cuit(cuit)

    d = datetime.now() - timedelta(seconds=random.randint(0, YEAR_SECONDS))

    return {
        "lead name": _messy_spaces(_messy_case(fake.name())),
        "company name": _messy_case(fake.company()),
        "cuit": cuit,
        "email": _messy_spaces(fake.email().upper() if random.random() < 0.3 else fake.email()),
        "phone": fake.phone_number(),
        "channel": _messy_case(random.choices(CHANNELS[0], weights=CHANNELS[1])[0]),
        "lead date": d.strftime(random.choice(DATE_FORMATS)),
        "status": random.choices(STATUSES[0], weights=STATUSES[1])[0],
        "owner": random.choice(OWNERS),
    }


def main() -> None:
    args = parser.parse_args()
    n_leads = args.rows or N_LEADS

    eng = engine()
    statement = select(Company.cuit).where(Company.is_supplier.is_(False))
    with Session(eng) as s:
        cuits = list(s.scalars(statement).all())

    rows = [_generate_row(cuits) for _ in range(n_leads)]

    # the same lead entered twice, which is what happens with a shared file
    for _ in range(int(n_leads * 0.05)):
        rows.append(dict(random.choice(rows)))
    random.shuffle(rows)

    pd.DataFrame(rows).to_excel(LEADS_FILE, index=False)

    print(f"seeded {len(rows)} leads")


if __name__ == "__main__":
    main()