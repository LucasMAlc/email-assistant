"""
Serviço de IA para classificação e geração de respostas
"""

import asyncio
from typing import Tuple
from openai import OpenAI
from app.core.config import settings
from app.core.exceptions import AIServiceError
from app.core.logging_config import logger


class AIService:
    """Serviço para interação com API de IA (DeepSeek)"""
    
    def __init__(self):
        """Inicializa cliente da API"""
        if not settings.DEEPSEEK_API_KEY:
            raise AIServiceError("DEEPSEEK_API_KEY não configurada")
        
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        
        logger.info("AIService inicializado com sucesso")
    
    def classify_email(self, text: str) -> Tuple[str, float, str]:
        """
        Classifica email em Produtivo ou Improdutivo
        
        Args:
            text: Conteúdo do email
        
        Returns:
            Tupla (categoria, confiança, método)
        """
        prompt = self._build_classification_prompt(text)
        
        try:
            response = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um classificador especializado em emails corporativos do setor financeiro. Responda APENAS com 'Produtivo' ou 'Improdutivo'."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            category = response.choices[0].message.content.strip()
            
            # Validar resposta
            if category not in ["Produtivo", "Improdutivo"]:
                logger.warning(f"Resposta inesperada da IA: {category}")
                # Fallback para classificação baseada em regras
                return self._classify_fallback(text)
            
            logger.info(f"Email classificado como: {category}")
            return category, 0.85, "deepseek"
        
        except Exception as e:
            logger.error(f"Erro na classificação via IA: {e}")
            # Fallback
            return self._classify_fallback(text)
    
    def generate_response(self, category: str, text: str) -> str:
        """
        Gera resposta automática baseada na categoria
        
        Args:
            category: Categoria do email (Produtivo/Improdutivo)
            text: Conteúdo original do email
        
        Returns:
            Resposta sugerida
        """
        prompt = self._build_response_prompt(category, text)
        
        try:
            response = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente de uma grande empresa do setor financeiro. Gere respostas formais, educadas e profissionais."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            generated_response = response.choices[0].message.content.strip()
            logger.info("Resposta gerada com sucesso")
            return generated_response
        
        except Exception as e:
            logger.error(f"Erro ao gerar resposta via IA: {e}")
            # Resposta padrão em caso de erro
            return self._get_default_response(category)
    
    def _build_classification_prompt(self, text: str) -> str:
        """Constrói prompt otimizado para classificação"""
        return f"""
Classifique o seguinte email corporativo em uma das categorias:

**PRODUTIVO**: Emails que requerem ação ou resposta
- Solicitações de suporte técnico
- Dúvidas sobre processos ou sistemas
- Atualizações sobre casos/requisições em andamento
- Pedidos de documentos ou informações
- Questões relacionadas a transações financeiras

**IMPRODUTIVO**: Emails que não requerem ação imediata
- Felicitações (aniversário, natal, etc)
- Mensagens de agradecimento genéricas
- Promoções comerciais
- Spam ou correntes
- Mensagens pessoais sem relação com trabalho

EMAIL:
{text[:1000]}

RESPONDA APENAS: "Produtivo" ou "Improdutivo"
"""
    
    def _build_response_prompt(self, category: str, text: str) -> str:
        """Constrói prompt para geração de resposta"""
        
        if category == "Produtivo":
            context = """
O email é PRODUTIVO (requer ação). Gere uma resposta formal que:
- Agradeça o contato
- Confirme o recebimento da solicitação
- Informe que a equipe irá analisar e responder em breve
- Seja educada e profissional
"""
        else:
            context = """
O email é IMPRODUTIVO (mensagem cordial). Gere uma resposta breve que:
- Agradeça a mensagem
- Seja cordial e amigável
- Mantenha formalidade corporativa
"""
        
        return f"""
{context}

EMAIL ORIGINAL:
{text[:500]}

Gere APENAS o corpo da resposta, sem assunto ou assinatura completa.
"""
    
    def _classify_fallback(self, text: str) -> Tuple[str, float, str]:
        """
        Classificação baseada em regras (fallback)
        
        Args:
            text: Texto do email
        
        Returns:
            Tupla (categoria, confiança, método)
        """
        text_lower = text.lower()
        
        # Palavras-chave para Improdutivo
        improdutivo_keywords = [
            'feliz', 'parabéns', 'aniversário', 'natal', 'ano novo',
            'promoção', 'desconto', 'oferta', 'grátis', 'compre já'
        ]
        
        # Palavras-chave para Produtivo
        produtivo_keywords = [
            'solicito', 'preciso', 'urgente', 'dúvida', 'problema',
            'suporte', 'ajuda', 'requisição', 'caso', 'atualização',
            'documento', 'relatório', 'transação', 'conta'
        ]
        
        # Contar ocorrências
        improdutivo_count = sum(1 for kw in improdutivo_keywords if kw in text_lower)
        produtivo_count = sum(1 for kw in produtivo_keywords if kw in text_lower)
        
        if improdutivo_count > produtivo_count:
            logger.info("Classificado como Improdutivo (fallback)")
            return "Improdutivo", 0.6, "rule-based"
        else:
            logger.info("Classificado como Produtivo (fallback)")
            return "Produtivo", 0.6, "rule-based"
    
    def _get_default_response(self, category: str) -> str:
        """Retorna resposta padrão em caso de erro na geração"""
        
        if category == "Produtivo":
            return """Prezado(a),

Agradecemos pelo seu contato.

Recebemos sua mensagem e nossa equipe já está analisando sua solicitação. Retornaremos com uma resposta detalhada em até 24 horas úteis.

Atenciosamente,
Equipe de Suporte"""
        else:
            return """Prezado(a),

Agradecemos pela sua mensagem!

Ficamos felizes com seu contato.

Atenciosamente,
Equipe"""