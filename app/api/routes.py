"""
Rotas da API
"""

from fastapi import APIRouter, Request, UploadFile, Form, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services import AIService, FileService, FeedbackService, TextProcessor
from app.core.logging_config import logger
from app.core.exceptions import FileValidationError, AIServiceError

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Instanciar serviços
ai_service = AIService()
file_service = FileService()
feedback_service = FeedbackService()
text_processor = TextProcessor()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página principal"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/process")
async def process_email(
    file: UploadFile = File(None),
    text: str = Form(None)
):
    """
    Processa email e retorna classificação + resposta
    
    Args:
        file: Arquivo .txt ou .pdf
        text: Texto direto do email
    
    Returns:
        JSON com resultado
    """
    try:
        content = ""
        
        # Extrair conteúdo
        if file and file.filename:
            logger.info(f"Processando arquivo: {file.filename}")
            content = await file_service.extract_text(file)
        
        elif text:
            logger.info("Processando texto direto")
            content = text.strip()
            
            if len(content) > 10000:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Texto muito longo. Máximo: 10.000 caracteres"}
                )
        
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Envie um arquivo ou texto"}
            )
        
        if not content:
            return JSONResponse(
                status_code=400,
                content={"error": "Não foi possível extrair conteúdo"}
            )
        
        # Classificar
        logger.info("Iniciando classificação...")
        category, confidence, method = ai_service.classify_email(content)
        
        # Gerar resposta
        logger.info("Gerando resposta...")
        response_text = ai_service.generate_response(category, content)
        
        # Preview do conteúdo
        content_preview = text_processor.truncate(content, 200)
        
        result = {
            "success": True,
            "category": category,
            "response": response_text,
            "confidence": confidence,
            "method": method,
            "content_preview": content_preview
        }
        
        logger.info(f"Processamento concluído: {category} ({confidence})")
        return JSONResponse(content=result)
    
    except FileValidationError as e:
        logger.warning(f"Erro de validação: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )
    
    except AIServiceError as e:
        logger.error(f"Erro no serviço de IA: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Erro ao processar com IA. Tente novamente."}
        )
    
    except Exception as e:
        logger.error(f"Erro inesperado: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Erro interno: {str(e)}"}
        )


@router.post("/feedback")
async def submit_feedback(
    original_text: str = Form(...),
    predicted: str = Form(...),
    feedback_type: str = Form(...),
    correction: str = Form(None)
):
    """
    Recebe feedback do usuário
    
    Args:
        original_text: Texto original do email
        predicted: Categoria prevista
        feedback_type: 'correct' ou 'incorrect'
        correction: Nova categoria (se incorrect)
    
    Returns:
        JSON com confirmação
    """
    try:
        feedback_data = {
            "original_text": original_text[:500],  # Limitar tamanho
            "predicted": predicted,
            "feedback_type": feedback_type,
            "correction": correction if feedback_type == "incorrect" else None
        }
        
        feedback_service.save_feedback(feedback_data)
        
        logger.info(f"Feedback recebido: {feedback_type}")
        
        return JSONResponse(content={
            "success": True,
            "message": "Feedback salvo com sucesso! Obrigado por nos ajudar a melhorar."
        })
    
    except Exception as e:
        logger.error(f"Erro ao salvar feedback: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Erro ao salvar feedback"}
        )


@router.get("/metrics")
async def get_metrics():
    """
    Retorna métricas da aplicação
    
    Returns:
        JSON com métricas
    """
    try:
        metrics = feedback_service.get_metrics()
        return JSONResponse(content=metrics)
    
    except Exception as e:
        logger.error(f"Erro ao buscar métricas: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Erro ao buscar métricas"}
        )


@router.get("/health")
async def health_check():
    """Health check para monitoramento"""
    return JSONResponse(content={
        "status": "ok",
        "service": "email-classifier",
        "version": "1.0.0"
    })