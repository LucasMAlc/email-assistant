# Email Assistant

Um assistente de emails que classifica mensagens como Produtivas ou Improdutivas e gera respostas automáticas usando a API DeepSeek.

## Funcionalidades

- Upload de arquivos .txt ou .pdf ou digitação manual do texto do email.

- Classificação automática do email (Produtivo / Improdutivo).

- Geração de resposta formal e educada ao email.

- Feedback do usuário, salvo em CSV (data/feedback.csv).

- Copiar resposta para o clipboard.

### Tecnologias

- Python 3.11+
- FastAPI
- Jinja2 (templates HTML)
- OpenAI SDK (DeepSeek API)
- NLTK (stopwords em português)
- pdfplumber (para leitura de PDFs)
- CSV (armazenamento de feedback)
- HTML/CSS/JS para frontend

## Configuração local

1. Clone o repositório:

'''bash
git clone https://github.com/LucasMAlc/email-assistant
cd email-assistant
'''

2. Crie e ative o ambiente virtual:

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

3. Instale as dependências:

pip install -r requirements.txt

4. Configure as variáveis de ambiente:
Crie um arquivo .env na raiz do projeto:

DEEPSEEK_API_KEY=your_deepseek_api_key
