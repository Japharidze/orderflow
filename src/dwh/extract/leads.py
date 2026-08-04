from collections.abc import Iterator

import pandas as pd

from dwh.config import LEADS_FILE


def leads() -> Iterator[list[dict]]:
    df = pd.read_excel(LEADS_FILE, dtype=str)
    df = df.astype(object).where(df.notna(), None) # convert NaN to None for all columns
    yield df.to_dict(orient="records") # yield a single batch of all leads, since the file is small