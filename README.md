# Email Assistant

Um assistente de emails que classifica mensagens como Produtivas ou Improdutivas e gera respostas automáticas usando a API DeepSeek.

Disponível em: [Email Assistant](https://email-assistant-1kk4.onrender.com)

### Funcionalidades

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

```bash
git clone https://github.com/LucasMAlc/email-assistant
cd email-assistant
```

2. Crie e ative o ambiente virtual:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
Crie um arquivo .env na raiz do projeto:

```bash
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### Rodar localmente

- Windows / Linux / macOS:

```bash
# Na raiz do projeto
bash start.sh
```
No Windows, você também pode executar o comando diretamente no terminal:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Acesse a aplicação em: http://localhost:8000

### Estrutura do projeto
```bash
email-assistant/
│
├─ app/
│  ├─ main.py          # FastAPI app
│  ├─ utils.py         # Funções de extração, classificação e geração de respostas
│
├─ templates/
│  └─ index.html       # Frontend
├─ static/
│  ├─ css/style.css    # CSS
│  └─ js/script.js     # Scripts
├─ data/
│  └─ feedback.csv     # Feedback salvos no .csv
├─ .env
├─ requirements.txt
├─ start.sh
└─ README.md
```