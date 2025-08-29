from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pdfplumber

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process", response_class=HTMLResponse)
async def process_email(request: Request, file: UploadFile = None, text: str = Form(None)):
    content = ""

    # Primeiro, checa se enviou texto
    if text and text.strip() != "":
        content = text
    # Depois checa se enviou arquivo
    elif file and file.filename != "":
        if file.filename.endswith(".txt"):
            content = (await file.read()).decode("utf-8")
        elif file.filename.endswith(".pdf"):
            with pdfplumber.open(file.file) as pdf:
                for page in pdf.pages:
                    content += page.extract_text() + "\n"
        else:
            content = "Formato não suportado."
    else:
        content = "Nenhum conteúdo fornecido."


    return templates.TemplateResponse("index.html", {"request": request, "content": content})
