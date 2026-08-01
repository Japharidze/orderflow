from collections.abc import Iterator

import pandas as pd

from dwh.config import LEADS_FILE


def extract_leads() -> Iterator[list[dict]]:
    df = pd.read_excel(LEADS_FILE, dtype=str)
    df = df.where(df["cuit"].notna(), None) # convert NaN to None for cuit, since it's optional
    yield df.to_dict(orient="records") # yield a single batch of all leads, since the file is small