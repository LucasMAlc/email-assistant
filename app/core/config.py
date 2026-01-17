"""
Configurações centralizadas da aplicação
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # API Configuration
    DEEPSEEK_API_KEY: str
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    AI_MODEL: str = "deepseek-chat"
    AI_TIMEOUT: int = 30
    
    # File Upload Limits
    MAX_FILE_SIZE: int = 2 * 1024 * 1024  # 2MB
    MAX_TEXT_LENGTH: int = 10000
    ALLOWED_EXTENSIONS: set = {".txt", ".pdf"}
    ALLOWED_MIME_TYPES: set = {"text/plain", "application/pdf"}
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_DIR: str = "uploads"
    FEEDBACK_FILE: str = "data/feedback.csv"
    
    # Application
    APP_NAME: str = "Email Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância única de Settings (Singleton)"""
    return Settings()


settings = get_settings()