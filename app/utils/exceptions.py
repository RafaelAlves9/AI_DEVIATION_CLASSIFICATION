
"""
Exceções customizadas para a aplicação
Hierarquia de exceções para tratamento granular de erros
"""


class DeviationClassifierError(Exception):
    """Exceção base para todas as exceções da aplicação"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self):
        """Converte exceção para dicionário"""
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'details': self.details
        }


class TranscriptionError(DeviationClassifierError):
    """Erro durante transcrição de áudio"""
    pass


class MLModelError(DeviationClassifierError):
    """Erro durante uso do modelo ML"""
    pass


class AIValidationError(DeviationClassifierError):
    """Erro durante validação com IA"""
    pass


class InvalidInputError(DeviationClassifierError):
    """Erro de validação de entrada"""
    pass
