
"""
Serviço de transcrição de áudio usando Faster-Whisper
Responsável por converter áudio em texto
"""
import tempfile
import os
from typing import Optional
from faster_whisper import WhisperModel
from app.utils.exceptions import TranscriptionError
from app.utils.logger import setup_logger


logger = setup_logger(__name__)


class TranscriptionService:
    """
    Serviço para transcrição de áudio usando Faster-Whisper (CTranslate2)
    
    Principles:
    - Single Responsibility: Apenas transcrição de áudio
    - Dependency Injection: Modelo pode ser injetado
    """
    
    def __init__(self, model_name: str = "medium"):
        """
        Inicializa o serviço de transcrição
        
        Args:
            model_name: Nome do modelo (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self._model = None
        logger.info(f"TranscriptionService inicializado com modelo: {model_name}")
    
    @property
    def model(self):
        """
        Lazy loading do modelo de transcrição
        Carrega apenas quando necessário para economizar memória
        """
        if self._model is None:
            logger.info(f"Carregando modelo Faster-Whisper: {self.model_name}")
            try:
                # Para CPU, compute_type int8 melhora performance com leve degradação de acurácia
                self._model = WhisperModel(
                    self.model_name,
                    device="cpu",
                    compute_type="int8"
                )
                logger.info("Modelo Faster-Whisper carregado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao carregar modelo Faster-Whisper: {str(e)}")
                raise TranscriptionError(
                    "Falha ao carregar modelo de transcrição",
                    details={'model': self.model_name, 'error': str(e)}
                )
        return self._model
    
    def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcreve áudio para texto
        
        Args:
            audio_bytes: Bytes do arquivo de áudio (MP3, WAV, etc)
            
        Returns:
            Texto transcrito
            
        Raises:
            TranscriptionError: Se houver erro na transcrição
        """
        if not audio_bytes:
            raise TranscriptionError("Áudio vazio fornecido")
        
        temp_file_path = None
        try:
            # Cria arquivo temporário para o áudio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            logger.info(f"Iniciando transcrição de áudio ({len(audio_bytes)} bytes)")
            
            # Transcreve usando Faster-Whisper
            segments, _info = self.model.transcribe(
                temp_file_path,
                language='pt',
                vad_filter=True
            )

            # Concatena texto de todos os segmentos
            transcribed_text = "".join(segment.text for segment in segments).strip()
            logger.info(f"Transcrição concluída: {len(transcribed_text)} caracteres")
            
            return transcribed_text
            
        except TranscriptionError:
            raise
        except Exception as e:
            logger.error(f"Erro inesperado na transcrição: {str(e)}")
            raise TranscriptionError(
                "Erro ao transcrever áudio",
                details={'error': str(e)}
            )
        finally:
            # Remove arquivo temporário
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception as e:
                    logger.warning(f"Não foi possível remover arquivo temporário: {e}")
    
    def is_available(self) -> bool:
        """
        Verifica se o serviço de transcrição está disponível
        
        Returns:
            True se disponível, False caso contrário
        """
        try:
            _ = self.model
            return True
        except Exception:
            return False
