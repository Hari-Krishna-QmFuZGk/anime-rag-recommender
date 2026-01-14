import os
from typing import List

from ingestion.jikan_client import fetch_anime_page
from ingestion.normalize import normalize_anime
from ingestion.persist import append_anime
from ingestion.schema import AnimeDocument
from utils.logger import Logging, LOG_FILE_CONSTANT
from utils.exceptions import AppError

START_PAGE = 1
END_PAGE = 100
BATCH_SIZE = 50

LOG_FILE = "ingestion"
os.environ[LOG_FILE_CONSTANT] = LOG_FILE
log = Logging(LOG_FILE)


def run_ingestion(start_page: int, end_page: int) -> None:
    """
    Incremental ingestion with intermediate persistence.
    Safe to crash and re-run.
    """

    log.info(f"Starting ingestion from page {start_page} to {end_page}")

    buffer: List[AnimeDocument] = []
    fetched = 0
    written = 0

    try:
        for page in range(start_page, end_page + 1):
            raw_records = fetch_anime_page(page)
            fetched += len(raw_records)

            for raw in raw_records:
                doc = normalize_anime(raw)
                if not doc:
                    continue

                buffer.append(doc)

                if len(buffer) >= BATCH_SIZE:
                    append_anime(buffer)
                    written += len(buffer)
                    buffer.clear()

            log.info(
                f"Page {page} processed | " f"fetched={fetched}, written={written}"
            )

        # flush remaining
        if buffer:
            append_anime(buffer)
            written += len(buffer)

        log.info(
            f"Ingestion complete | "
            f"fetched={fetched}, written={written}, "
            f"dropped={fetched - written}"
        )

    except AppError:
        log.exception("Ingestion failed due to application error")
        raise

    except Exception:
        log.exception("Ingestion failed due to unexpected error")
        raise


if __name__ == "__main__":
    run_ingestion(START_PAGE, END_PAGE)
