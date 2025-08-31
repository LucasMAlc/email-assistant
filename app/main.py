from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil
import os

from app.utils import extract_text_from_file, classify_email, generate_response

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process", response_class=HTMLResponse)
async def process_email(request: Request, file: UploadFile = None, text: str = Form(None)):
    content = ""
    error = None

    try:
        # Validação de entrada
        if file and file.filename != "":
            filepath = os.path.join(UPLOAD_DIR, file.filename)

            # Valida tamanho do arquivo
            file.file.seek(0, os.SEEK_END)
            size = file.file.tell()
            file.file.seek(0)
            if size > 2 * 1024 * 1024:  # 2MB
                error = "Arquivo muito grande. Limite: 2MB."
                return templates.TemplateResponse("index.html", {"request": request, "error": error})

            # Salva e processa
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            with open(filepath, "rb") as f:
                content = extract_text_from_file(f, file.filename)
        elif text:
            content = text.strip()
        else:
            error = "Nenhum conteúdo fornecido."
            return templates.TemplateResponse("index.html", {"request": request, "error": error})

        if not content:
            error = "Não foi possível processar o texto."
            return templates.TemplateResponse("index.html", {"request": request, "error": error})

        # Classificação e resposta
        categoria, confianca, fonte = classify_email(content)
        resposta = generate_response(categoria)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "content": content,
            "categoria": categoria,
            "confianca": round(confianca, 2),
            "fonte": fonte,
            "resposta": resposta
        })

    except Exception as e:
        error = f"Ocorreu um erro: {str(e)}"
        return templates.TemplateResponse("index.html", {"request": request, "error": error})


@app.post("/feedback")
async def feedback(original_text: str = Form(...), predicted: str = Form(...),
                   correction: str = Form(...), new_category: str = Form("")):
    try:
        with open("feedback.csv", "a", encoding="utf-8") as f:
            f.write(f"{original_text};{predicted};{correction};{new_category}\n")
        return JSONResponse({"message": "Feedback recebido. Obrigado!"})
    except Exception:
        return JSONResponse({"message": "Erro ao salvar feedback."}, status_code=500)
