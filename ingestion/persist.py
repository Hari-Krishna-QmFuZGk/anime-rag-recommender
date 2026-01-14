import os
import json
from pathlib import Path
from typing import Iterable, List

from ingestion.schema import AnimeDocument
from utils.exceptions import DataPersistenceError
from utils.logger import Logging, LOG_FILE_CONSTANT

log = Logging(os.getenv(LOG_FILE_CONSTANT, "ingestion"))

_DATA_DIR = Path(__file__).parent.parent / "data"
_ANIME_FILE = _DATA_DIR / "anime.jsonl"


def append_anime(anime: Iterable[AnimeDocument]) -> None:
    """
    Append anime documents to JSONL file.
    Safe for long-running ingestion jobs.
    """
    try:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)

        with _ANIME_FILE.open("a", encoding="utf-8") as f:
            for doc in anime:
                f.write(json.dumps(doc.model_dump(), ensure_ascii=False))
                f.write("\n")

        log.info("Appended anime records to JSONL")

    except Exception as exc:
        log.exception("Failed to append anime data")
        raise DataPersistenceError(
            "Failed to append anime data",
            cause=exc,
        )


def load_anime() -> List[AnimeDocument]:
    """
    Load anime documents from JSONL file.
    """
    try:
        if not _ANIME_FILE.exists():
            log.warning("Anime JSONL file does not exist")
            return []

        anime: List[AnimeDocument] = []

        with _ANIME_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    anime.append(AnimeDocument.model_validate_json(line))

        log.info(f"Loaded {len(anime)} anime records from JSONL")

        return anime

    except Exception as exc:
        log.exception("Failed to load anime data")
        raise DataPersistenceError(
            "Failed to load anime data",
            cause=exc,
        )
