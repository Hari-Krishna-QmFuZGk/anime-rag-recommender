from typing import List, Optional
from pydantic import BaseModel, Field


class AnimeDocument(BaseModel):
    """
    Canonical anime representation used across the system.
    """

    id: int = Field(..., description="MyAnimeList anime ID")
    title: str
    synopsis: str

    genres: List[str] = []
    themes: List[str] = []

    studio: Optional[str] = None
    score: Optional[float] = None
    year: Optional[int] = None
    episodes: Optional[int] = None

    class Config:
        frozen = True  # Immutable once created
