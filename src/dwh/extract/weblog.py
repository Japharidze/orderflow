import re

from collections.abc import Iterator

from dwh.config import WEBLOG_FILE

BATCH = 5000
LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) (?P<ident>\S+) (?P<username>\S+) \[(?P<requested_at>[^\]]+)\] '
    r'"(?P<request>[^"]*)" (?P<status>\S+) (?P<size>\S+) '
    r'"(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
)

def _parse_weblog_line(line: str) -> dict:
    """Parse a single line of the weblog into a dictionary."""
    match = LOG_PATTERN.match(line)
    return match.groupdict() if match else {}

def extract_weblog() -> Iterator[list[dict]]:
    """Yield batches of weblog rows so memory stays flat."""
    batch = []
    with open(WEBLOG_FILE) as f:
        for line in f:
            batch.append(_parse_weblog_line(line.strip("\n")))
            if len(batch) >= BATCH:
                yield batch
                batch = []
    if batch:
        yield batch