import os
from typing import List

from sentence_transformers import SentenceTransformer
from utils.logger import Logging, LOG_FILE_CONSTANT
from utils.exceptions import EmbeddingError

log = Logging(os.getenv(LOG_FILE_CONSTANT, "indexing"))

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load once per process (important)
_model = SentenceTransformer(_MODEL_NAME)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Convert a list of texts into embeddings using a HuggingFace model.
    """

    if not texts:
        return []

    try:
        log.info(f"Embedding {len(texts)} chunks with {_MODEL_NAME}")

        embeddings = _model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,  # VERY important for cosine similarity
        )

        return embeddings.tolist()

    except Exception as exc:
        log.exception("Embedding generation failed")
        raise EmbeddingError(
            "Failed to generate embeddings",
            cause=exc,
            context={"count": len(texts)},
        )
