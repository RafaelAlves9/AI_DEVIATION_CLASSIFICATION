"""
Serviço principal de classificação de desvios
Orquestra todos os outros serviços para executar o fluxo completo
"""
from typing import Optional
from app.models.schemas import DeviationClassification, ClassificationRequest
from app.services.transcription_service import TranscriptionService
from app.services.ml_model_service import MLModelService
from app.services.ai_validation_service import AIValidationService
from app.utils.exceptions import InvalidInputError
from app.utils.logger import setup_logger


logger = setup_logger(__name__)


class DeviationClassificationService:
    """
    Serviço orquestrador para classificação de desvios
    
    Principles:
    - Single Responsibility: Orquestração do fluxo de classificação
    - Dependency Injection: Todos os serviços são injetados
    - Open/Closed: Pode adicionar novos serviços sem modificar o fluxo
    
    Fluxo:
    1. Valida entrada
    2. Transcreve áudio (se houver)
    3. Concatena textos
    4. Classifica com modelo ML
    5. Valida/corrige com IA
    6. Retorna classificação final
    """
    
    def __init__(
        self,
        transcription_service: TranscriptionService = None,
        ml_service: MLModelService = None,
        ai_service: AIValidationService = None
    ):
        """
        Inicializa o serviço de classificação
        
        Args:
            transcription_service: Serviço de transcrição (opcional, criado se None)
            ml_service: Serviço de ML (opcional, criado se None)
            ai_service: Serviço de validação IA (opcional, criado se None)
        """
        self.transcription_service = transcription_service or TranscriptionService()
        self.ml_service = ml_service or MLModelService()
        self.ai_service = ai_service or AIValidationService()
        
        logger.info("DeviationClassificationService inicializado")
    
    def classify(self, request: ClassificationRequest) -> DeviationClassification:
        """
        Classifica um desvio seguindo todo o fluxo
        
        Args:
            request: Dados da requisição (description, audio, local)
            
        Returns:
            DeviationClassification com a classificação final
            
        Raises:
            InvalidInputError: Se entrada for inválida
            TranscriptionError: Se falhar transcrição
            MLModelError: Se falhar classificação ML
            AIValidationError: Se falhar validação IA
        """
        # 1. Valida entrada
        self._validate_request(request)
        
        logger.info(f"Iniciando classificação de desvio para local: {request.local}")
        
        # 2. Transcreve áudio se houver
        transcription = ""
        if request.audio:
            logger.info("Áudio detectado - iniciando transcrição")
            transcription = self.transcription_service.transcribe(request.audio)
            logger.info(f"Transcrição concluída: '{transcription}'")
        
        # 3. Concatena descrição + transcrição
        text_parts = []
        if request.description:
            text_parts.append(request.description)
        if transcription:
            text_parts.append(transcription)
        
        if not text_parts:
            raise InvalidInputError(
                "Nenhum conteúdo fornecido (descrição ou áudio)",
                details={'local': request.local}
            )
        
        full_text = " ".join(text_parts)
        logger.info(f"Texto completo para análise: '{full_text}'")
        
        # 4. Classifica com modelo ML
        logger.info("Classificando com modelo ML")
        ml_classification = self.ml_service.classify(full_text, request.local)
        logger.info(f"Classificação ML: {ml_classification.to_dict()}")
        
        # 5. Valida e corrige com IA
        logger.info("Validando com IA (Abacus.AI)")
        final_classification = self.ai_service.validate_and_correct(
            full_text,
            request.local,
            ml_classification
        )
        logger.info(f"Classificação final: {final_classification.to_dict()}")
        
        return final_classification
    
    def _validate_request(self, request: ClassificationRequest):
        """
        Valida requisição de classificação
        
        Args:
            request: Requisição para validar
            
        Raises:
            InvalidInputError: Se requisição for inválida
        """
        # Valida local (obrigatório)
        if not request.local or not request.local.strip():
            raise InvalidInputError(
                "Campo 'local' é obrigatório",
                details={'request': request.to_dict()}
            )
        
        # Valida que há pelo menos descrição ou áudio
        if not request.description and not request.audio:
            raise InvalidInputError(
                "Deve fornecer pelo menos 'description' ou 'audio'",
                details={'local': request.local}
            )
        
        # Valida descrição se fornecida
        if request.description and not request.description.strip():
            raise InvalidInputError(
                "Campo 'description' não pode ser vazio",
                details={'local': request.local}
            )
        
        # Valida áudio se fornecido
        if request.audio and len(request.audio) == 0:
            raise InvalidInputError(
                "Campo 'audio' não pode ser vazio",
                details={'local': request.local}
            )
        
        logger.debug("Requisição validada com sucesso")
    
    def health_check(self) -> dict:
        """
        Verifica status de saúde de todos os serviços
        
        Returns:
            Dicionário com status de cada serviço
        """
        return {
            'transcription_service': self.transcription_service.is_available(),
            'ml_service': self.ml_service.is_available(),
            'ai_validation_service': self.ai_service.is_available()
        }
