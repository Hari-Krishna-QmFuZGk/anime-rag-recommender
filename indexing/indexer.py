import os
from typing import List, Dict

import chromadb
from chromadb.config import Settings

from ingestion.persist import load_anime
from indexing.chunking import build_semantic_chunks
from indexing.embedding import embed_texts
from utils.logger import Logging, LOG_FILE_CONSTANT
from utils.exceptions import IndexingError

log = Logging(os.getenv(LOG_FILE_CONSTANT, "indexing"))

_CHROMA_DIR = "chroma_db"
_COLLECTION_NAME = "anime_chunks"

_client = chromadb.Client(
    Settings(
        persist_directory=_CHROMA_DIR,
        anonymized_telemetry=False,
    )
)

_collection = _client.get_or_create_collection(_COLLECTION_NAME)


def index_anime() -> None:
    """
    Build vector index from ingested anime data.
    """

    log.info("Loading ingested anime data")
    anime_docs = load_anime()

    if not anime_docs:
        log.warning("No anime data found to index")
        return None

    texts: List[str] = []
    metadatas: List[Dict] = []
    ids: List[str] = []

    for anime in anime_docs:
        chunks = build_semantic_chunks(anime)

        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            metadatas.append(
                {
                    "anime_id": anime.id,
                    "title": anime.title,
                }
            )
            ids.append(f"{anime.id}_{i}")

    log.info(f"Prepared {len(texts)} chunks for embedding")

    try:
        embeddings = embed_texts(texts)

        log.info("Storing embeddings in Chroma")

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
