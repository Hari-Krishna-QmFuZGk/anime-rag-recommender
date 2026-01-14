from typing import Optional


class AppError(Exception):
    """
    Base exception for the application.

    All custom exceptions should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        *,
        cause: Optional[Exception] = None,
        context: Optional[dict] = None,
    ):
        super().__init__(message)
        self.message = message
        self.cause = cause
        self.context = context or {}

    def __str__(self):
        base = self.message
        if self.context:
            base += f" | context={self.context}"
        if self.cause:
            base += f" | cause={repr(self.cause)}"
        return base


# =========================
# Ingestion Exceptions
# =========================


class IngestionError(AppError):
    """Raised when data ingestion fails."""


class JikanAPIError(IngestionError):
    """Raised when Jikan API calls fail."""


class DataNormalizationError(IngestionError):
    """Raised when raw data cannot be normalized."""


class DataPersistenceError(IngestionError):
    """Raised when saving or loading data fails."""


# =========================
# Indexing Exceptions
# =========================


class IndexingError(AppError):
    """Raised during embedding or indexing failures."""


class EmbeddingError(IndexingError):
    """Raised when embedding generation fails."""


class VectorStoreError(IndexingError):
    """Raised when vector DB operations fail."""


# =========================
# Retrieval Exceptions
# =========================


class RetrievalError(AppError):
    """Raised during retrieval failures."""


class PromptError(RetrievalError):
    """Raised when prompt construction fails."""


class LLMInvocationError(RetrievalError):
    """Raised when LLM inference fails."""


# =========================
# Configuration Exceptions
# =========================


class ConfigurationError(AppError):
    """Raised when required configuration is missing or invalid."""
