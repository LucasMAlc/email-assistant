"""
Exceções customizadas da aplicação
"""


class EmailProcessingError(Exception):
    """Erro base para processamento de emails"""
    pass


class FileValidationError(EmailProcessingError):
    """Erro na validação de arquivo"""
    pass


class AIServiceError(EmailProcessingError):
    """Erro ao chamar serviço de IA"""
    pass


class TextProcessingError(EmailProcessingError):
    """Erro no processamento de texto"""
    pass


class FeedbackError(EmailProcessingError):
    """Erro ao salvar feedback"""
    pass