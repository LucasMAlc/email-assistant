"""
Core module - Configurações e utilitários centrais
"""

from .config import settings
from .exceptions import (
    EmailProcessingError,
    FileValidationError,
    AIServiceError
)

__all__ = [
    "settings",
    "EmailProcessingError",
    "FileValidationError",
    "AIServiceError"
]