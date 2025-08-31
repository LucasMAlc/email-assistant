import re
import pdfplumber
import nltk
from nltk.corpus import stopwords
from transformers import pipeline
import os
import requests

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
# Classificador local
# -----------------------------
CLASSIFIER = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    top_k=1 
)

def classify_email(text: str):
    """Classifica email como 'Produtivo' ou 'Improdutivo'."""
    result = CLASSIFIER(text[:500])[0]
    label = result["label"]
    text_lower = text.lower()
    
    if label == "LABEL_0":  # Negativo -> Produtivo
        categoria = "Produtivo"
    elif label == "LABEL_2":  # Positivo -> palavras sociais
        if any(word in text_lower for word in ["obrigado", "parabens", "feliz", "agradec"]):
            categoria = "Improdutivo"
        else:
            categoria = "Produtivo"
    else:
        categoria = "Produtivo"  # Neutro
    
    return categoria, 1.0, "local_model"


# -----------------------------
# Gerador de respostas via API Gemma
# -----------------------------
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/google/gemma-3-270m"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def generate_response(category: str, text: str) -> str:
    """Gera resposta ao email usando Gemma 3 270M via API."""
    prompt = f"Responda ao seguinte email: {text[:200]}"
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 150, "temperature": 0.7}
    }
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if isinstance(result, list) and result:
            generated_text = result[0].get("generated_text", "")
            response_text = generated_text[len(prompt):].strip()
            return response_text if response_text else "Obrigado pelo contato!"
        
        return "Não foi possível gerar uma resposta."
    
    except Exception as e:
        print(f"Erro ao gerar resposta via API: {e}")
        return "Ocorreu um erro ao tentar gerar a resposta."
