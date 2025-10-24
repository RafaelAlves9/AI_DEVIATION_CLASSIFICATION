
"""
Schemas de dados para requisições e respostas
"""
from dataclasses import dataclass, asdict
from typing import Optional
from .enums import DeviationType, DeviationCategory, DeviationDirectioning


@dataclass
class ClassificationRequest:
    """Schema para requisição de classificação"""
    local: str
    description: Optional[str] = None
    audio: Optional[bytes] = None
    
    def to_dict(self):
        """Converte para dicionário"""
        return asdict(self)


@dataclass
class DeviationClassification:
    """Schema para resultado da classificação"""
    gravidade: float  # 0.0 a 1.0
    urgencia: float   # 0.0 a 1.0
    tendencia: float  # 0.0 a 1.0
    tipo: DeviationType
    direcionamento: DeviationDirectioning
    categoria: DeviationCategory
    
    def to_dict(self):
        """Converte para dicionário com enums como strings"""
        return {
            'gravidade': self.gravidade,
            'urgencia': self.urgencia,
            'tendencia': self.tendencia,
            'tipo': self.tipo.value,
            'direcionamento': self.direcionamento.value,
            'categoria': self.categoria.value
        }
    
    def __post_init__(self):
        """Valida os valores após inicialização"""
        # Valida ranges
        if not 0.0 <= self.gravidade <= 1.0:
            raise ValueError("Gravidade deve estar entre 0.0 e 1.0")
        if not 0.0 <= self.urgencia <= 1.0:
            raise ValueError("Urgência deve estar entre 0.0 e 1.0")
        if not 0.0 <= self.tendencia <= 1.0:
            raise ValueError("Tendência deve estar entre 0.0 e 1.0")
        
        # Converte strings para enums se necessário
        if isinstance(self.tipo, str):
            self.tipo = DeviationType(self.tipo)
        if isinstance(self.direcionamento, str):
            self.direcionamento = DeviationDirectioning(self.direcionamento)
        if isinstance(self.categoria, str):
            self.categoria = DeviationCategory(self.categoria)
