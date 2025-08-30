import re
import nltk
from nltk.corpus import stopwords
import pdfplumber

# Baixar stopwords do NLTK (executar uma vez)
nltk.download('stopwords')
stop_words = set(stopwords.words('portuguese'))

def preprocess_text(text: str) -> str:
    """Limpa e normaliza o texto para melhorar a classificação"""
    text = text.lower()
    text = re.sub(r'[^a-zá-ú0-9\s]', '', text)
    tokens = [word for word in text.split() if word not in stop_words]
    return ' '.join(tokens)

def extract_text_from_file(file, filename: str) -> str:
    """Extrai texto de arquivos .txt ou .pdf"""
    content = ""
    if filename.endswith(".txt"):
        content = file.decode("utf-8")
    elif filename.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                content += page.extract_text() + "\n"
    else:
        content = "Formato não suportado."
    return content

def classify_email(text: str) -> tuple:
    """
    Classificação híbrida:
    - Se regras baterem, retorna alta confiança
    - Caso contrário, usa modelo ML (simulado)
    """
    text = preprocess_text(text)

    regras_produtivo = ["projeto", "relatorio", "prazo", "entrega", "reuniao", "orcamento", "solicitar", "urgente"]
    regras_improdutivo = ["promocao", "oferta", "desconto", "feliz natal", "boas festas"]

    for palavra in regras_produtivo:
        if palavra in text:
            return "Produtivo", 0.99, "rule"

    for palavra in regras_improdutivo:
        if palavra in text:
            return "Improdutivo", 0.99, "rule"

    # Se nenhuma regra bateu, usa modelo ML (simulado)
    return classify_email_ml(text)

def classify_email_ml(text: str) -> tuple:
    """
    Simulação de modelo de Machine Learning (aqui ainda é simples)
    """
    # Exemplo: só para simular, ajusta confiança baseado no comprimento
    if len(text.split()) > 10:
        return "Produtivo", 0.75, "model"
    else:
        return "Improdutivo", 0.60, "model"

def generate_response(category: str) -> str:
    """Sugere uma resposta baseada na categoria"""
    if category == "Produtivo":
        return "Obrigado pelo contato! Vamos analisar as informações e retornaremos em breve."
    else:
        return "Obrigado pela mensagem! Registramos o seu contato. Se precisar de algo mais, estamos à disposição."
