import os
import time
from typing import List

from jikanpy import Jikan
from tenacity import retry, stop_after_attempt, wait_exponential

from utils.logger import Logging, _OS_LOG_FILE_CONSTANT
from utils.exceptions import JikanAPIError

LOG_FILE = os.getenv(_OS_LOG_FILE_CONSTANT, "ingestion")
log = Logging(LOG_FILE)

# Jikan client
jikan = Jikan()

# Safe rate limit: ~2–3 req/sec
_RATE_LIMIT_SLEEP = 0.4


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, max=10),
)
def fetch_anime_page(page: int) -> List[dict]:
    """
    Fetch a page of anime records using Jikan search endpoint.

    Args:
        page: Page number (1-indexed)

    Returns:
        List of raw anime dictionaries

    Raises:
        JikanAPIError
    """
    try:
        log.info(f"Fetching anime search page={page}")

        response = jikan.search(
            "anime",
            "",
            page=page,
        )

        data = response.get("data", [])

        if not isinstance(data, list):
            raise JikanAPIError(
                "Unexpected Jikan search response type",
                context={
                    "page": page,
                    "data_type": type(data).__name__,
                },
            )

        if not data:
            log.warning(f"No anime returned for search page={page}")

        return data

    except Exception as exc:
        log.exception("Jikan search request failed")
        raise JikanAPIError(
            "Failed to fetch anime search page from Jikan",
            cause=exc,
            context={"page": page},
        )


def fetch_anime_pages(start_page: int, end_page: int) -> List[dict]:
    """
    Fetch multiple pages of anime records via search.

    Returns:
        Flattened list of raw anime dicts
    """
    if start_page < 1 or end_page < start_page:
        raise ValueError("Invalid page range")

    all_records: List[dict] = []

    for page in range(start_page, end_page + 1):
        records = fetch_anime_page(page)
        all_records.extend(records)
        time.sleep(_RATE_LIMIT_SLEEP_SECONDS)

    log.info(f"Fetched {len(all_records)} anime records from pages {start_page}–{end_page}")

    return all_records
