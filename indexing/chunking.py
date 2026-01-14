from typing import List

from ingestion.schema import AnimeDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Shared splitter for long fields
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def build_semantic_chunks(anime: AnimeDocument) -> List[str]:
    """
    Create field-aware semantic chunks for an anime.

    Each chunk represents a different semantic view:
    - Narrative (synopsis)
    - Taste profile (genres, themes, studio, score, year)
    """

    chunks: List[str] = []

    if anime.synopsis:
        synopsis_chunks = _splitter.split_text(
            f"Title: {anime.title}\nSynopsis: {anime.synopsis}"
        )
        chunks.extend(synopsis_chunks)

    taste_parts = []

    if anime.genres:
        taste_parts.append(f"Genres: {', '.join(anime.genres)}")

    if anime.themes:
        taste_parts.append(f"Themes: {', '.join(anime.themes)}")

    if anime.studio:
        taste_parts.append(f"Studio: {anime.studio}")

    if anime.year:
        taste_parts.append(f"Year: {anime.year}")

    if anime.score:
        taste_parts.append(f"Score: {anime.score}")

    if taste_parts:
        chunks.append(" | ".join(taste_parts))

    return chunks
