"""
Schemas Pydantic para validação de dados
"""

from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import Optional


class EmailCategory(str, Enum):
    """Categorias de classificação de emails"""
    PRODUTIVO = "Produtivo"
    IMPRODUTIVO = "Improdutivo"


class EmailClassificationRequest(BaseModel):
    """Request para classificação de email"""
    content: str = Field(..., min_length=10, max_length=10000)
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError("Conteúdo não pode ser vazio")
        return v.strip()


class EmailClassificationResponse(BaseModel):
    """Response da classificação"""
    success: bool
    category: EmailCategory
    response: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    method: str
    content_preview: Optional[str] = None


class FeedbackRequest(BaseModel):
    """Request para envio de feedback"""
    original_text: str
    predicted: EmailCategory
    feedback_type: str = Field(..., pattern="^(correct|incorrect)$")
    correction: Optional[EmailCategory] = None
    
    @validator('correction')
    def validate_correction(cls, v, values):
        if values.get('feedback_type') == 'incorrect' and not v:
            raise ValueError("Correção é obrigatória quando feedback é 'incorrect'")
        return v


class FeedbackResponse(BaseModel):
    """Response do feedback"""
    success: bool
    message: str