"""
Serviço de modelo ML para classificação de desvios
Responsável por carregar e usar o modelo de ML
"""
import pickle
import os
from typing import Dict
from app.utils.exceptions import MLModelError
from app.utils.logger import setup_logger
from app.models.schemas import DeviationClassification
from app.models.enums import GravityLevel, UrgencyLevel, TrendLevel


logger = setup_logger(__name__)


class MLModelService:
    """
    Serviço para classificação usando modelo ML
    
    Principles:
    - Single Responsibility: Apenas predição com ML
    - Open/Closed: Pode ser extendido com novos modelos sem modificar
    - Dependency Inversion: Depende de abstração (modelo com método predict)
    """
    
    def __init__(self, model_path: str = "models_data/deviation_classifier.pkl"):
        """
        Inicializa o serviço de ML
        
        Args:
            model_path: Caminho para o arquivo .pkl do modelo
        """
        self.model_path = model_path
        self._model = None
        logger.info(f"MLModelService inicializado com modelo: {model_path}")
    
    @property
    def model(self):
        """
        Lazy loading do modelo ML
        Carrega apenas quando necessário
        """
        if self._model is None:
            logger.info(f"ML carregar: path={self.model_path}")
            try:
                if not os.path.exists(self.model_path):
                    raise MLModelError(
                        f"Arquivo de modelo não encontrado: {self.model_path}",
                        details={'path': self.model_path}
                    )
                
                with open(self.model_path, 'rb') as f:
                    self._model = pickle.load(f)
                
                logger.info("ML pronto")
                
                # Valida que o modelo tem método predict
                if not hasattr(self._model, 'predict'):
                    raise MLModelError(
                        "Modelo não possui método 'predict'",
                        details={'path': self.model_path}
                    )
                    
            except MLModelError:
                raise
            except Exception as e:
                logger.error(f"Erro ao carregar modelo ML: {str(e)}")
                raise MLModelError(
                    "Falha ao carregar modelo ML",
                    details={'path': self.model_path, 'error': str(e)}
                )
        return self._model
    
    def classify(self, text: str, location: str) -> DeviationClassification:
        """
        Classifica desvio usando modelo ML
        
        Args:
            text: Texto concatenado (descrição + transcrição)
            location: Local do desvio
            
        Returns:
            DeviationClassification com a classificação
            
        Raises:
            MLModelError: Se houver erro na classificação
        """
        if not text or not text.strip():
            raise MLModelError("Texto vazio fornecido para classificação")
        
        if not location or not location.strip():
            raise MLModelError("Local não fornecido para classificação")
        
        try:
            logger.info(f"ML classificar: local={location}")
            logger.debug(f"ML texto={text[:100]}...")
            
            # Usa o modelo para predizer (retorna estrutura flat)
            prediction = self.model.predict(text, location)
            
            logger.info(f"ML ok: {prediction}")
            
            # Cria objeto a partir da predição flat
            classification = DeviationClassification(**prediction)
            
            return classification
            
        except MLModelError:
            raise
        except ValueError as e:
            logger.error(f"ML inválido: {str(e)}")
            raise MLModelError(
                "Classificação inválida retornada pelo modelo",
                details={'error': str(e), 'prediction': prediction}
            )
        except Exception as e:
            logger.error(f"ML erro: {str(e)}")
            raise MLModelError(
                "Erro ao classificar desvio com modelo ML",
                details={'error': str(e)}
            )
    
    def is_available(self) -> bool:
        """
        Verifica se o serviço ML está disponível
        
        Returns:
            True se disponível, False caso contrário
        """
        try:
            _ = self.model
            return True
        except Exception:
            return False
