"""
Models module - Schemas Pydantic para validação
"""

from .schemas import (
    EmailClassificationRequest,
    EmailClassificationResponse,
    FeedbackRequest,
    FeedbackResponse,
    EmailCategory
)

__all__ = [
    "EmailClassificationRequest",
    "EmailClassificationResponse",
    "FeedbackRequest",
    "FeedbackResponse",
    "EmailCategory"
]