# app/utils.py
import re
import os
from io import BytesIO
from typing import Tuple
import joblib

# modelo opcional (se você treinar depois, coloque em models/tfidf.joblib e models/clf.joblib)
MODEL_TFIDF_PATH = os.path.join("models", "tfidf.joblib")
MODEL_CLF_PATH = os.path.join("models", "clf.joblib")

# lista simples de stopwords PT (pode estender)
_PT_STOPWORDS = {
    "e","a","o","que","de","do","da","em","um","para","com","na","no","por","se",
    "os","as","dos","das","um","uma","é","não","ao","como","mais","já","ou","sua",
    "seu","meu","minha","você","vc","por favor","porfavor"
}

# palavras chave
_PRODUCTIVE_KEYWORDS = [
    "status","Solicit","solicit","solicita","requisit","protocolo","ticket",
    "erro","problema","ajuda","suporte","anexo","comprovante","fatura","pagamento",
    "vencimento","boleto","atualiza","atualização","reclama","cancelar","contrato",
    "documento","cadastro","alterar","consulta","renovação","restauração","login"
]
_IMPRODUCTIVE_KEYWORDS = [
    "obrigad","obrigada","valeu","boa sorte","feliz","parabéns","congratul","ótimo",
    "bom dia","boa tarde","boa noite","gratidão","feliz natal","feliz ano"
]

def preprocess(text: str) -> str:
    text = (text or "").strip()
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    text = text.lower()
    text = re.sub(r"[^\w\s#@\-]", " ", text)  # keep # and @ and - for tokens
    text = re.sub(r"\b\d{2,}\b", lambda m: m.group(0), text)
    return text

def detect_protocol(text: str) -> str | None:
    # tenta pegar algo como #1234 ou protocolo 1234 ou nr 1234
    patterns = [r"#\d{3,7}", r"protocolo\s*[:\-]?\s*(\d{3,7})", r"\bnr\.?\s*(\d{3,7})"]
    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE)
        if m:
            return m.group(0)
    return None

def rule_based_score(text: str) -> Tuple[str, float]:
    """
    Retorna (label, confidence) baseado em contagem simples de keywords.
    Confidence entre 0.5 e 0.99 dependendo da diferença.
    """
    txt = preprocess(text)
    prod = 0
    imp = 0
    for kw in _PRODUCTIVE_KEYWORDS:
        if kw in txt:
            prod += 1
    for kw in _IMPRODUCTIVE_KEYWORDS:
        if kw in txt:
            imp += 1
    if prod == 0 and imp == 0:
        # sem hits, baixa confiança — assume produtivo (é mais seguro tratar como produtivo)
        return "Produtivo", 0.6
    if prod >= imp:
        diff = prod - imp
        conf = min(0.6 + 0.15 * diff, 0.98)
        return "Produtivo", round(conf, 2)
    else:
        diff = imp - prod
        conf = min(0.6 + 0.15 * diff, 0.98)
        return "Improdutivo", round(conf, 2)

def load_model():
    """Tenta carregar modelo TFIDF+clf se existir. Retorna (tfidf, clf) ou (None,None)."""
    try:
        if os.path.exists(MODEL_TFIDF_PATH) and os.path.exists(MODEL_CLF_PATH):
            tfidf = joblib.load(MODEL_TFIDF_PATH)
            clf = joblib.load(MODEL_CLF_PATH)
            return tfidf, clf
    except Exception:
        pass
    return None, None

def classify(text: str) -> Tuple[str, float, str]:
    """
    Retorna (label, confidence, source)
    source: "model" ou "rules"
    """
    tfidf, clf = load_model()
    txt = preprocess(text)
    if tfidf and clf:
        try:
            X = tfidf.transform([txt])
            proba = clf.predict_proba(X)[0]
            idx = proba.argmax()
            label = clf.classes_[idx]
            conf = float(proba[idx])
            return label, round(conf, 2), "model"
        except Exception:
            pass
    # fallback para regras
    label, conf = rule_based_score(txt)
    return label, conf, "rules"

def generate_response(raw_text: str, category: str) -> str:
    txt = preprocess(raw_text)
    protoc = detect_protocol(raw_text) or detect_protocol(txt)
    if category == "Produtivo":
        if protoc:
            return (f"Recebemos sua mensagem. Localizei o protocolo {protoc}. "
                    "Vamos analisar e retornaremos em breve. Se possível, confirme se os anexos foram enviados.")
        # detecta menção a anexo
        if "anex" in txt:
            return ("Obrigado pelo envio. Não localizei protocolo — poderia confirmar o número do chamado ou reenviar o anexo? "
                    "Assim conseguimos avançar na análise.")
        return ("Obrigado pelo contato. Para que possamos analisar, poderia informar o número do protocolo/ticket e anexar documentos se houver?")
    else:
        return ("Obrigado pela mensagem! Registramos o seu contato. Se precisar de algo mais, estamos à disposição.")
