"""
Serviço para extração de texto de arquivos
"""

import os
from typing import BinaryIO
from fastapi import UploadFile
import pdfplumber
from app.core.config import settings
from app.core.exceptions import FileValidationError
from app.core.logging_config import logger


class FileService:
    """Serviço para manipulação de arquivos"""
    
    def __init__(self):
        # Criar diretório de uploads se não existir
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        logger.info("FileService inicializado")
    
    async def validate_file(self, file: UploadFile) -> None:
        """
        Valida arquivo antes do processamento
        
        Args:
            file: Arquivo enviado
        
        Raises:
            FileValidationError: Se arquivo for inválido
        """
        # Verifica se arquivo foi enviado
        if not file or not file.filename:
            raise FileValidationError("Nenhum arquivo foi enviado")
        
        # Verifica extensão
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise FileValidationError(
                f"Extensão '{ext}' não permitida. Use: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Verifica tamanho
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)
        
        if size > settings.MAX_FILE_SIZE:
            size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            raise FileValidationError(
                f"Arquivo muito grande. Tamanho máximo: {size_mb}MB"
            )
        
        logger.info(f"Arquivo validado: {file.filename} ({size} bytes)")
    
    async def extract_text(self, file: UploadFile) -> str:
        """
        Extrai texto do arquivo
        
        Args:
            file: Arquivo enviado
        
        Returns:
            Texto extraído
        
        Raises:
            FileValidationError: Se não conseguir extrair texto
        """
        await self.validate_file(file)
        
        filename = file.filename.lower()
        
        try:
            if filename.endswith('.txt'):
                content = await file.read()
                text = content.decode('utf-8')
                logger.info(f"Texto extraído de TXT: {len(text)} caracteres")
                return text
            
            elif filename.endswith('.pdf'):
                text = await self._extract_from_pdf(file)
                logger.info(f"Texto extraído de PDF: {len(text)} caracteres")
                return text
            
            else:
                raise FileValidationError("Formato de arquivo não suportado")
        
        except UnicodeDecodeError:
            raise FileValidationError("Erro ao decodificar arquivo. Verifique a codificação.")
        
        except Exception as e:
            logger.error(f"Erro ao extrair texto: {e}")
            raise FileValidationError(f"Erro ao processar arquivo: {str(e)}")
    
    async def _extract_from_pdf(self, file: UploadFile) -> str:
        """
        Extrai texto de PDF
        
        Args:
            file: Arquivo PDF
        
        Returns:
            Texto extraído
        """
        content = ""
        
        try:
            # Salvar temporariamente (pdfplumber precisa de arquivo)
            temp_path = os.path.join(settings.UPLOAD_DIR, f"temp_{file.filename}")
            
            with open(temp_path, "wb") as f:
                f.write(await file.read())
            
            # Extrair texto
            with pdfplumber.open(temp_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text + "\n"
            
            # Remover arquivo temporário
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if not content.strip():
                raise FileValidationError("PDF não contém texto extraível")
            
            return content
        
        except Exception as e:
            logger.error(f"Erro ao extrair PDF: {e}")
            raise FileValidationError(f"Erro ao processar PDF: {str(e)}")
    
    def save_file(self, file: UploadFile) -> str:
        """
        Salva arquivo no diretório de uploads
        
        Args:
            file: Arquivo a ser salvo
        
        Returns:
            Caminho do arquivo salvo
        """
        filepath = os.path.join(settings.UPLOAD_DIR, file.filename)
        
        with open(filepath, "wb") as f:
            f.write(file.file.read())
        
        logger.info(f"Arquivo salvo: {filepath}")
        return filepath