from collections import defaultdict
from typing import List, Dict
from pathlib import Path

import chromadb
from chromadb.config import Settings

from indexing.embedding import embed_texts
from utils.logger import Logging
from utils.exceptions import RetrievalError

from retrieval.filters import build_where
from retrieval.hybrid import bm25_score
from retrieval.rerank import rerank

log = Logging("retrieval")

_CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
_COLLECTION_NAME = "anime_chunks"

_client = chromadb.PersistentClient(
    path=_CHROMA_DIR,
    settings=Settings(
        anonymized_telemetry=False,
    ),
)

_collection = _client.get_or_create_collection(_COLLECTION_NAME)


def _match_tags(meta, include_genres, exclude_genres, include_themes, exclude_themes):
    genres = meta["genres"].split("|") if meta["genres"] else []
    themes = meta["themes"].split("|") if meta["themes"] else []

    if include_genres and not set(include_genres).issubset(genres):
        return False
    if exclude_genres and set(exclude_genres) & set(genres):
        return False
    if include_themes and not set(include_themes).issubset(themes):
        return False
    if exclude_themes and set(exclude_themes) & set(themes):
        return False

    return True


def search(query: str, top_k: int = 10, filters: Dict = None) -> List[Dict]:
    """
    Search anime recommendations for a user query.
    """

    try:
        log.info(f"Searching for: {query}")

        query_embedding = embed_texts([query])[0]

        where = build_where(**filters) if filters else None

        filters = filters or {}

        include_genres = filters.get("include_genres")
        exclude_genres = filters.get("exclude_genres")
        include_themes = filters.get("include_themes")
        exclude_themes = filters.get("exclude_themes")

        results = _collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 10,
            where=where,
        )

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]

        bm25 = bm25_score(query, docs)

        anime_scores = {}
        anime_titles = {}

        for meta, dist, bm in zip(metas, dists, bm25):
            if not _match_tags(
                meta, include_genres, exclude_genres, include_themes, exclude_themes
            ):
                continue
            anime_id = meta["anime_id"]
            anime_titles[anime_id] = meta["title"]

            score = (1 / (1 + dist)) + 0.3 * bm
            anime_scores[anime_id] = anime_scores.get(anime_id, 0) + score

        ranked = sorted(anime_scores.items(), key=lambda x: x[1], reverse=True)

        candidates = [
            {"anime_id": aid, "title": anime_titles[aid], "score": score}
            for aid, score in ranked[:15]
        ]

        return rerank(query, candidates)

    except Exception as exc:
        log.exception("Search failed")
        raise RetrievalError(
            "Failed to search anime",
            cause=exc,
            context={"query": query},
        )
