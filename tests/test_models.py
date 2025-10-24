
"""
Testes para models e schemas
"""
import pytest
from app.models.schemas import DeviationClassification, ClassificationRequest
from app.models.enums import DeviationType, DeviationCategory, DeviationDirectioning


class TestDeviationClassification:
    """Testes para DeviationClassification"""
    
    def test_creation_with_valid_data(self, sample_classification_data):
        """Testa criação com dados válidos"""
        classification = DeviationClassification(**sample_classification_data)
        
        assert classification.gravidade == 0.6
        assert classification.urgencia == 0.5
        assert classification.tipo == DeviationType.SEGURANCA
        
    def test_creation_with_invalid_gravidade(self):
        """Testa criação com gravidade inválida"""
        with pytest.raises(ValueError, match="Gravidade deve estar entre"):
            DeviationClassification(
                gravidade=1.5,
                urgencia=0.5,
                tendencia=0.4,
                tipo='seguranca',
                direcionamento='seguranca_trabalho',
                categoria='medio'
            )
    
    def test_to_dict(self, sample_classification_data):
        """Testa conversão para dicionário"""
        classification = DeviationClassification(**sample_classification_data)
        result = classification.to_dict()
        
        assert isinstance(result, dict)
        assert result['tipo'] == 'seguranca'
        assert result['gravidade'] == 0.6


class TestClassificationRequest:
    """Testes para ClassificationRequest"""
    
    def test_creation_with_required_field(self):
        """Testa criação com campo obrigatório"""
        request = ClassificationRequest(local="Setor 1")
        assert request.local == "Setor 1"
        assert request.description is None
        assert request.audio is None
    
    def test_to_dict(self, sample_request_data):
        """Testa conversão para dicionário"""
        request = ClassificationRequest(**sample_request_data)
        result = request.to_dict()
        
        assert isinstance(result, dict)
        assert result['local'] == 'Setor 3'
