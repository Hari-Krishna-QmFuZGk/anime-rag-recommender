import os
from typing import List, Dict
from pathlib import Path

import chromadb
from chromadb.config import Settings

from ingestion.persist import load_anime
from indexing.chunking import build_semantic_chunks
from indexing.embedding import embed_texts
from utils.logger import Logging, LOG_FILE_CONSTANT
from utils.exceptions import IndexingError

log = Logging(os.getenv(LOG_FILE_CONSTANT, "indexing"))

_CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
_COLLECTION_NAME = "anime_chunks"

_client = chromadb.PersistentClient(
    path=_CHROMA_DIR,
    settings=Settings(
        anonymized_telemetry=False,
    ),
)


_collection = _client.get_or_create_collection(_COLLECTION_NAME)


def _safe_str(x):
    return str(x) if x is not None else ""


def _safe_int(x):
    return int(x) if x is not None else -1


def _safe_float(x):
    return float(x) if x is not None else -1.0


def _pipe(xs):
    return "|".join(xs) if xs else ""


def _prepare_chunks(anime_docs: List) -> tuple:
    texts: List[str] = []
    metadatas: List[Dict] = []
    ids: List[str] = []

    for anime in anime_docs:
        chunks = build_semantic_chunks(anime)

        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            chunk_type = (
                "taste" if ("Genres:" in chunk or "Themes:" in chunk) else "narrative"
            )

            metadatas.append(
                {
                    "anime_id": _safe_int(anime.id),
                    "title": _safe_str(anime.title),
                    "genres": _pipe(anime.genres),
                    "themes": _pipe(anime.themes),
                    "studio": _safe_str(anime.studio),
                    "year": _safe_int(anime.year),
                    "score": _safe_float(anime.score),
                    "chunk_type": chunk_type,
                }
            )
            ids.append(f"{anime.id}_{i}")

    return texts, metadatas, ids


def _upsert_batches(
    texts: List[str], embeddings: List, metadatas: List[Dict], ids: List[str]
) -> None:
    batch_size = 5000
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        batch_embeddings = embeddings[i : i + batch_size]
        batch_metadatas = metadatas[i : i + batch_size]
        batch_ids = ids[i : i + batch_size]

        _collection.add(
            documents=batch_texts,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas,
            ids=batch_ids,
        )


def index_anime() -> None:
    """
    Build vector index from ingested anime data.
    """

    log.info("Loading ingested anime data")
    anime_docs = load_anime()

    if not anime_docs:
        log.warning("No anime data found to index")
        return None

    texts, metadatas, ids = _prepare_chunks(anime_docs)

    log.info(f"Prepared {len(texts)} chunks for embedding")

    try:
        embeddings = embed_texts(texts)

        log.info("Storing embeddings in Chroma")
        _upsert_batches(texts, embeddings, metadatas, ids)

        log.info("Indexing complete")

    except Exception as exc:
        log.exception("Indexing failed")
        raise IndexingError(
            "Failed to index anime",
            cause=exc,
            context={"chunks": len(texts)},
        )


if __name__ == "__main__":
    index_anime()
