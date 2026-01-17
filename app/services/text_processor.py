"""
Processamento de texto com NLP
"""

import re
import nltk
from typing import List
from app.core.config import settings
from app.core.logging_config import logger

# Download de recursos NLTK (apenas uma vez)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords


class TextProcessor:
    """Processador de texto com NLP"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('portuguese'))
        logger.info("TextProcessor inicializado")
    
    def preprocess(self, text: str) -> str:
        """
        Pré-processa texto: lowercase, remove caracteres especiais, stopwords
        
        Args:
            text: Texto bruto
        
        Returns:
            Texto processado
        """
        try:
            # Lowercase
            text = text.lower()
            
            # Remove caracteres especiais (mantém letras, números e espaços)
            text = re.sub(r"[^a-zá-úà-ù0-9\s]", "", text)
            
            # Remove stopwords
            tokens = [
                word for word in text.split() 
                if word not in self.stop_words and len(word) > 2
            ]
            
            processed = " ".join(tokens)
            logger.debug(f"Texto processado: {len(processed)} caracteres")
            
            return processed
            
        except Exception as e:
            logger.error(f"Erro no pré-processamento: {e}")
            return text  # Retorna texto original em caso de erro
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extrai palavras-chave mais frequentes
        
        Args:
            text: Texto processado
            top_n: Número de palavras a retornar
        
        Returns:
            Lista de palavras-chave
        """
        from collections import Counter
        
        words = text.split()
        word_freq = Counter(words)
        
        return [word for word, _ in word_freq.most_common(top_n)]
    
    def truncate(self, text: str, max_length: int = 1000) -> str:
        """
        Trunca texto mantendo palavras completas
        
        Args:
            text: Texto original
            max_length: Tamanho máximo
        
        Returns:
            Texto truncado
        """
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            truncated = truncated[:last_space]
        
        return truncated + "..."