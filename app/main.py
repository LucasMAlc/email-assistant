from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.responses import HTMLResponse
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

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process", response_class=HTMLResponse)
async def process_email(request: Request, file: UploadFile = None, text: str = Form(None)):
    content = ""

    if file:
        filepath = os.path.join(UPLOAD_DIR, file.filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        with open(filepath, "rb") as f:
            content = extract_text_from_file(f, file.filename)
    elif text:
        content = text
    else:
        content = "Nenhum conteúdo fornecido."

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

@app.post("/feedback")
async def feedback(original_text: str = Form(...), predicted: str = Form(...),
                   correction: str = Form(...), new_category: str = Form("")):
    with open("feedback.csv", "a", encoding="utf-8") as f:
        f.write(f"{original_text};{predicted};{correction};{new_category}\n")
    return {"message": "Feedback recebido. Obrigado!"}
