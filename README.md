# 📧 Email Assistant - Classificador Inteligente

Sistema de classificação automática de emails com IA para empresas do setor financeiro. Classifica emails em **Produtivo** ou **Improdutivo** e gera respostas automáticas personalizadas.

## 🎯 Funcionalidades

- ✅ Classificação automática de emails usando IA (DeepSeek)
- ✅ Geração de respostas personalizadas
- ✅ Upload de arquivos (.txt, .pdf) ou entrada de texto direto
- ✅ Interface moderna com drag-and-drop
- ✅ Sistema de feedback para melhoria contínua
- ✅ API RESTful completa

## 🛠️ Tecnologias

**Backend:**
- Python 3.9+
- FastAPI
- Pydantic
- OpenAI SDK (DeepSeek API)
- NLTK
- pdfplumber
- Pandas

**Frontend:**
- HTML5, CSS3, JavaScript
- Design responsivo

## 📁 Estrutura do Projeto
```
email-assistant/
├── app/
│   ├── core/          # Configurações e logging
│   ├── models/        # Schemas Pydantic
│   ├── services/      # Lógica de negócio (IA, arquivos, feedback)
│   └── api/           # Rotas da API
├── static/            # CSS e JavaScript
├── templates/         # HTML
└── data/              # Dados de feedback
```

## 🚀 Como Rodar Localmente

### **Pré-requisitos**
- Python 3.9 ou superior
- Conta na [DeepSeek](https://www.deepseek.com/) para obter API key

### **Instalação**
```bash
# 1. Clone o repositório
git clone <seu-repositorio>
cd email-assistant

# 2. Crie um ambiente virtual
python -m venv venv

# 3. Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Configure as variáveis de ambiente
# Crie um arquivo .env na raiz do projeto:
DEEPSEEK_API_KEY=sua_chave_aqui
DEBUG=False

# 6. Execute a aplicação
python -m app.main
```

Acesse: **http://localhost:8000**

## 📡 Endpoints da API

- `GET /` - Interface web
- `POST /process` - Classificar email
- `POST /feedback` - Enviar feedback
- `GET /metrics` - Obter métricas
- `GET /health` - Health check

## 🌐 Deploy

**Aplicação em produção:** [\[Link do deploy aqui\]](https://email-assistant-1kk4.onrender.com/)

A aplicação está hospedada no Render com deploy automático via GitHub.
