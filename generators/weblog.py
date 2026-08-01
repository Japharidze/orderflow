import random
import argparse
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy import select
from sqlalchemy.orm import Session

from dwh.db.models import Company, engine
from dwh.config import SOURCE

parser = argparse.ArgumentParser()
parser.add_argument('--lines', type=int, help="Number")
fake = Faker("es_AR")
Faker.seed(42)
random.seed(42)


N_LOGS = 500
YEAR_SECONDS = int(3.154e7)

COUNTRY_BLOCKS = {          # country_code: first two octet
    "AR": "200.45", "BR": "177.12", "CL": "190.98",
    "US": "104.16", "ES": "88.24",  "MX": "187.33",
}
COUNTRY_WEIGHTS = [1, 5, 1, 1, 1, 1]   # BR dominates, so report 2 has a clear winner

METHODS = (["GET", "POST", "PUT", "DELETE"], [80, 15, 3, 2])
STATUSES = ([200, 201, 301, 302, 400, 401, 403, 404, 500, 503],
            [70, 5, 4, 5, 3, 3, 2, 5, 2, 1])

def _broke_line(log: str) -> str:
    methods = [_truncated, _missing_fields, _unclosed_quote, _junk, _not_malformed] # TBD
    log = random.choice(methods)(log)
    return log

def _generate_line(user: str, country: str) -> str:
        # "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\""

        # generate ip from the country range
        h = f"{COUNTRY_BLOCKS[country]}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        ident = "-"


        # random time from past 12 months = 7,777K seconds
        t = datetime.now() - timedelta(seconds=random.randint(0, YEAR_SECONDS))
        t = t.strftime("%d/%b/%Y:%H:%M:%S +0000")

        # HTTP Request details
        method = random.choices(METHODS[0], weights=METHODS[1])[0]
        uri = fake.uri_path()
        r = f"{method} /{uri} HTTP/1.1"

        # status code
        s = random.choices(STATUSES[0], weights=STATUSES[1])[0]

        b = random.randint(100, 10000)

        referer = fake.uri()

        user_agent = fake.user_agent()

        return f"{h} {ident} {user} [{t}] \"{r}\" {s} {b} \"{referer}\" \"{user_agent}\""

def main() -> None:
    args = parser.parse_args()
    n_logs = args.lines or N_LOGS
    eng = engine()
    statement = select(Company.user_name) # both companies and suppliers are here
    with Session(eng) as s:
        users = s.scalars(statement).all()
    user_pool = list(users) + ["-"] * 8 + [fake.user_name() for _ in range(5)]

    # each user has a home country, so a company's logins cluster in one place
    home = {u: random.choices(list(COUNTRY_BLOCKS), weights=COUNTRY_WEIGHTS)[0]
            for u in user_pool}

    p = SOURCE / "weblog.txt"
    with open(p, mode='w') as f:
        for _ in range(n_logs):
            # get random (user: country) pair from companies or suppliers, or "-" from anonymous
            u = random.choice(user_pool)
            line = _generate_line(u, home[u])
            if random.random() < 0.02:
                line = line #_broke_line(line)

            f.write(line + '\n')

    print(f"seeded {n_logs} lines")

if __name__ == "__main__":
    main()