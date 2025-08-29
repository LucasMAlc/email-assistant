from fastapi import FastAPI, Request, UploadFile, Form, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from io import BytesIO
import pdfplumber
from .utils import preprocess, classify, generate_response
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
async def process_email(request: Request, file: UploadFile | None = File(None), text: str | None = Form(None)):
    content = ""

    # Prioriza texto colado
    if text and text.strip():
        content = text.strip()
    elif file and getattr(file, "filename", ""):
        fname = file.filename.lower()
        raw = await file.read()  # bytes
        if fname.endswith(".txt"):
            try:
                content = raw.decode("utf-8")
            except:
                content = raw.decode("latin-1", errors="ignore")
        elif fname.endswith(".pdf"):
            try:
                with pdfplumber.open(BytesIO(raw)) as pdf:
                    pages = [p.extract_text() or "" for p in pdf.pages]
                    content = "\n".join(pages).strip()
            except Exception as e:
                content = ""
        else:
            content = ""
    else:
        content = ""

    if not content:
        return templates.TemplateResponse("index.html", {"request": request, "content": "", "error": "Nenhum conteúdo extraído (PDF pode ser imagem/escaneado)."})
    # classify + generate
    label, conf, source = classify(content)
    suggestion = generate_response(content, label)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "content": content,
        "category": label,
        "confidence": conf,
        "source": source,
        "suggestion": suggestion
    })