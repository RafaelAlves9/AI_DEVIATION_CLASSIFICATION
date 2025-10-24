
"""
Schemas de dados para requisições e respostas
"""
from dataclasses import dataclass, asdict
from typing import Optional
from .enums import (
    DeviationType, DeviationCategory, DeviationDirectioning,
    GravityLevel, UrgencyLevel, TrendLevel
)


@dataclass
class ClassificationRequest:
    """Schema para requisição de classificação"""
    local: str
    description: Optional[str] = None
    audio: Optional[bytes] = None
    
    def to_dict(self):
        """Converte para dicionário"""
        return asdict(self)
    
    def __post_init__(self):
        """Valida os valores após inicialização"""
        # Validação para garantir que pelo menos um dos campos opcionais foi preenchido
        if self.description is None and self.audio is None:
            raise ValueError("Pelo menos 'description' ou 'audio' deve ser fornecido.")


@dataclass
class DeviationClassification:
    """Schema para resultado da classificação"""
    gravidade: GravityLevel
    urgencia: UrgencyLevel
    tendencia: TrendLevel
    tipo: DeviationType
    direcionamento: DeviationDirectioning
    categoria: DeviationCategory

    def to_dict(self):
        """Converte para dicionário com enums como inteiros"""
        return {
            'gravidade': self.gravidade.value,
            'urgencia': self.urgencia.value,
            'tendencia': self.tendencia.value,
            'tipo': self.tipo.value,
            'direcionamento': self.direcionamento.value,
            'categoria': self.categoria.value
        }

    def __post_init__(self):
        """Valida os valores após inicialização"""
        # Converte inteiros para enums se necessário
        if isinstance(self.gravidade, int):
            self.gravidade = GravityLevel(self.gravidade)
        if isinstance(self.urgencia, int):
            self.urgencia = UrgencyLevel(self.urgencia)
        if isinstance(self.tendencia, int):
            self.tendencia = TrendLevel(self.tendencia)
        if isinstance(self.tipo, int):
            self.tipo = DeviationType(self.tipo)
        if isinstance(self.direcionamento, int):
            self.direcionamento = DeviationDirectioning(self.direcionamento)
        if isinstance(self.categoria, int):
            self.categoria = DeviationCategory(self.categoria)
