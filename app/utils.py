import os
import re
import pdfplumber
import nltk
from nltk.corpus import stopwords
import requests
import json
from dotenv import load_dotenv

# -----------------------------
# Carrega variáveis do .env
# -----------------------------
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("A chave OPENROUTER_API_KEY não foi encontrada. Verifique seu arquivo .env")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "deepseek/deepseek-chat-v3-0324:free"

# -----------------------------
# Setup NLTK
# -----------------------------
nltk.download("stopwords", quiet=True)
STOP_WORDS = set(stopwords.words("portuguese"))

# -----------------------------
# Pré-processamento de texto
# -----------------------------
def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-zá-ú0-9\s]", "", text)
    tokens = [word for word in text.split() if word not in STOP_WORDS]
    return " ".join(tokens)

# -----------------------------
# Extração de texto de arquivos
# -----------------------------
def extract_text_from_file(file, filename: str) -> str:
    if filename.endswith(".txt"):
        return file.read().decode("utf-8")
    elif filename.endswith(".pdf"):
        content = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    content += page_text + "\n"
        return content
    return "Formato não suportado."

# -----------------------------
# Classificação com DeepSeek
# -----------------------------
def classify_email(text: str):
    """Classifica email usando DeepSeek via OpenRouter."""
    prompt = f"""
    Analise o seguinte email e classifique em uma das categorias:
    - Produtivo
    - Improdutivo
    
    Email:
    {text[:500]}
    
    Responda apenas com a categoria.
    """
    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": "Você é um assistente especializado em classificação de emails."},
                    {"role": "user", "content": prompt}
                ]
            }),
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        
        category = result["choices"][0]["message"]["content"].strip()
        return category, 1.0, "deepseek"
    except Exception as e:
        print(f"Erro ao classificar via API: {e}")
        return "Erro", 0.0, "error"

# -----------------------------
# Geração de resposta com DeepSeek
# -----------------------------
def generate_response(category: str, text: str) -> str:
    """Gera resposta ao email usando DeepSeek via OpenRouter."""
    prompt = f"""
    Você é um assistente que responde emails de forma educada.
    Categoria do email: {category}
    Email original:
    {text[:1000]}

    Escreva uma resposta clara e formal.
    """
    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": "Você é um assistente especializado em escrever emails formais."},
                    {"role": "user", "content": prompt}
                ]
            }),
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        
        answer = result["choices"][0]["message"]["content"].strip()
        return answer if answer else "Obrigado pelo contato!"
    except Exception as e:
        print(f"Erro ao gerar resposta via API: {e}")
        return "Ocorreu um erro ao tentar gerar a resposta."
