"""
Serviço para gerenciamento de feedback
"""

import csv
import os
import pandas as pd
from datetime import datetime
from typing import Dict, Optional
from app.core.config import settings
from app.core.exceptions import FeedbackError
from app.core.logging_config import logger


class FeedbackService:
    """Serviço para gerenciar feedback dos usuários"""
    
    def __init__(self):
        """Inicializa serviço e garante que diretório existe"""
        self.feedback_file = settings.FEEDBACK_FILE
        os.makedirs(os.path.dirname(self.feedback_file), exist_ok=True)
        logger.info("FeedbackService inicializado")
    
    def save_feedback(self, feedback_data: Dict) -> None:
        """
        Salva feedback do usuário
        
        Args:
            feedback_data: Dicionário com dados do feedback
        
        Raises:
            FeedbackError: Se não conseguir salvar
        """
        try:
            # Adicionar metadados
            feedback_data['timestamp'] = datetime.now().isoformat()
            feedback_data['app_version'] = settings.APP_VERSION
            
            file_exists = os.path.isfile(self.feedback_file)
            
            with open(self.feedback_file, mode='a', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'timestamp', 'original_text', 'predicted', 
                    'feedback_type', 'correction', 'app_version'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(feedback_data)
            
            logger.info(f"Feedback salvo: {feedback_data['feedback_type']}")
        
        except Exception as e:
            logger.error(f"Erro ao salvar feedback: {e}")
            raise FeedbackError(f"Não foi possível salvar feedback: {str(e)}")
    
    def get_metrics(self) -> Dict:
        """
        Calcula métricas baseadas no feedback
        
        Returns:
            Dicionário com métricas
        """
        if not os.path.exists(self.feedback_file):
            return {
                "total_feedbacks": 0,
                "accuracy": None,
                "correct_count": 0,
                "incorrect_count": 0,
                "distribution": {}
            }
        
        try:
            df = pd.read_csv(self.feedback_file)
            
            total = len(df)
            correct = len(df[df['feedback_type'] == 'correct'])
            incorrect = len(df[df['feedback_type'] == 'incorrect'])
            
            accuracy = (correct / total * 100) if total > 0 else None
            
            # Distribuição de categorias
            distribution = {}
            if 'predicted' in df.columns:
                distribution = df['predicted'].value_counts().to_dict()
            
            metrics = {
                "total_feedbacks": total,
                "accuracy": round(accuracy, 2) if accuracy else None,
                "correct_count": correct,
                "incorrect_count": incorrect,
                "distribution": distribution
            }
            
            logger.info(f"Métricas calculadas: {metrics}")
            return metrics
        
        except Exception as e:
            logger.error(f"Erro ao calcular métricas: {e}")
            return {
                "error": str(e),
                "total_feedbacks": 0
            }
    
    def get_recent_feedbacks(self, limit: int = 10) -> list:
        """
        Retorna feedbacks mais recentes
        
        Args:
            limit: Número máximo de feedbacks
        
        Returns:
            Lista de feedbacks
        """
        if not os.path.exists(self.feedback_file):
            return []
        
        try:
            df = pd.read_csv(self.feedback_file)
            recent = df.tail(limit).to_dict('records')
            return recent
        
        except Exception as e:
            logger.error(f"Erro ao buscar feedbacks recentes: {e}")
            return []