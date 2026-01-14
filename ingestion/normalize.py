import os
from typing import Optional

from ingestion.schema import AnimeDocument
from utils.exceptions import DataNormalizationError
from utils.logger import Logging, LOG_FILE_CONSTANT

log = Logging(os.getenv(LOG_FILE_CONSTANT, "ingestion"))


def normalize_anime(raw: dict) -> Optional[AnimeDocument]:
    """
    Normalize raw Jikan anime JSON into AnimeDocument.

    Returns:
        AnimeDocument if valid
        None if the record should be skipped (non-fatal)

    Raises:
        DataNormalizationError for unexpected / corrupt data
    """

    try:
        synopsis = raw.get("synopsis") or ""
        synopsis = synopsis.strip()

        # Hard drop: no meaningful text → useless for RAG
        if not synopsis:
            log.warning(
                "Dropping anime with empty synopsis",
            )
            return None

        anime_id = raw.get("mal_id")
        title = raw.get("title")

        if not anime_id or not title:
            log.warning(
                "Dropping anime due to missing id or title",
            )
            return None

        return AnimeDocument(
            id=anime_id,
            title=title,
            synopsis=synopsis,
            genres=[g["name"] for g in raw.get("genres", [])],
            themes=[t["name"] for t in raw.get("themes", [])],
            studio=(raw["studios"][0]["name"] if raw.get("studios") else None),
            score=raw.get("score"),
            year=raw.get("year"),
            episodes=raw.get("episodes"),
        )

    except Exception as e:
        # This is a true error — not just bad data
        log.exception("Failed to normalize anime record")
        raise DataNormalizationError(
            "Failed to normalize raw anime data",
            cause=e,
            context={
                "raw_keys": list(raw.keys()),
                "mal_id": raw.get("mal_id"),
            },
        )
