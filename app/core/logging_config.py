"""
Configuração de logging profissional
"""

import logging
import sys
from datetime import datetime


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configura sistema de logging
    
    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    
    # Criar logger
    logger = logging.getLogger("email_assistant")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Formato do log
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo (opcional)
    try:
        file_handler = logging.FileHandler(
            f'logs/app_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        pass  # Se não conseguir criar arquivo, continua só com console
    
    return logger


# Instância global do logger
logger = setup_logging()