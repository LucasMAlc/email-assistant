# train_model.py
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import csv

# Exemplo: cria um dataset simples se não houver arquivo
data = [
    ("Preciso do status do chamado #1234, enviei comprovante", "Produtivo"),
    ("Quando será a cobrança? tenho problema no pagamento", "Produtivo"),
    ("Feliz aniversário! tudo de bom", "Improdutivo"),
    ("Obrigado pela ajuda, ótimo suporte", "Improdutivo"),
    ("Erro no login, não consigo acessar", "Produtivo"),
    ("Boas festas e sucesso", "Improdutivo"),
]

# Se você tiver data/samples.csv com colunas (text,label), carregue aqui
texts, y = zip(*data)
tfidf = TfidfVectorizer(ngram_range=(1,2), min_df=1)
X = tfidf.fit_transform(texts)
clf = LogisticRegression(max_iter=1000)
clf.fit(X, y)

os.makedirs("models", exist_ok=True)
joblib.dump(tfidf, os.path.join("models", "tfidf.joblib"))
joblib.dump(clf, os.path.join("models", "clf.joblib"))

print("Modelo treinado e salvo em models/")
