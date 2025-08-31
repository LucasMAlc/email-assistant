import csv
import os
import re
import pdfplumber
import nltk
from nltk.corpus import stopwords
from dotenv import load_dotenv
from openai import OpenAI

# -----------------------------
# Carrega .env
# -----------------------------
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("A chave DEEPSEEK_API_KEY não foi encontrada no .env")

# Cliente DeepSeek
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# -----------------------------
# NLTK e stopwords
# -----------------------------
nltk.download("stopwords", quiet=True)
STOP_WORDS = set(stopwords.words("portuguese"))

# -----------------------------
# Pré-processamento
# -----------------------------
def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-zá-ú0-9\s]", "", text)
    tokens = [word for word in text.split() if word not in STOP_WORDS]
    return " ".join(tokens)

# -----------------------------
# Extração de texto
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
# Classificação e resposta via DeepSeek
# -----------------------------
def classify_email(text: str) -> tuple:
    """Classifica email como Produtivo ou Improdutivo usando DeepSeek."""
    prompt = f"""
    Classifique o seguinte email em uma das categorias: Produtivo ou Improdutivo. 
    Produtivo: Relacionados à trabalho e solicitações importantes.
    Improdutivo: Felicitações, promoções, aniversários, etc.
    Email:
    {text[:1000]}
    Responda apenas com a categoria.
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em classificação de emails."},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        category = response.choices[0].message.content.strip()
        return category, 1.0, "deepseek"
    except Exception as e:
        print(f"Erro ao classificar via DeepSeek: {e}")
        return "Erro", 0.0, "error"

def generate_response(category: str, text: str) -> str:
    """Gera resposta ao email usando DeepSeek."""
    prompt = f"""
            Você é um assistente de uma grande empresa financeira que responde emails de forma formal e educada.
            Categoria do email: {category}
            Email original:
            {text[:1000]}
            Responda somente com o corpo do email.
            """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em responder emails."},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erro ao gerar resposta via DeepSeek: {e}")
        return "Ocorreu um erro ao tentar gerar a resposta."

FEEDBACK_FILE = os.path.join("data", "feedback.csv")

def save_feedback(original_text: str, predicted: str, correction: str, new_category: str = ""):
    """Salva feedback do usuário em CSV."""
    os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
    file_exists = os.path.isfile(FEEDBACK_FILE)
    
    with open(FEEDBACK_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["original_text", "predicted", "correction", "new_category"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "original_text": original_text,
            "predicted": predicted,
            "correction": correction,
            "new_category": new_category
        })
