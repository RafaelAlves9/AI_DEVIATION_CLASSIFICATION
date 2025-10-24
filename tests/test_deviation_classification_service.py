
"""
Testes para DeviationClassificationService
"""
import pytest
from app.services.deviation_classification_service import DeviationClassificationService
from app.models.schemas import ClassificationRequest
from app.utils.exceptions import InvalidInputError


class TestDeviationClassificationService:
    """Testes para DeviationClassificationService"""
    
    def test_health_check(self):
        """Testa health check"""
        service = DeviationClassificationService()
        status = service.health_check()
        
        assert isinstance(status, dict)
        assert 'ml_service' in status
        assert status['ml_service'] is True
    
    def test_classify_with_description_only(self):
        """Testa classificação apenas com descrição"""
        service = DeviationClassificationService()
        request = ClassificationRequest(
            local="Setor 1",
            description="Problema grave de segurança detectado"
        )
        
        result = service.classify(request)
        
        assert result is not None
        assert 0.0 <= result.gravidade <= 1.0
        assert result.tipo is not None
    
    def test_validate_request_without_local(self):
        """Testa validação sem local"""
        service = DeviationClassificationService()
        request = ClassificationRequest(local="", description="Teste")
        
        with pytest.raises(InvalidInputError, match="'local' é obrigatório"):
            service._validate_request(request)
    
    def test_validate_request_without_content(self):
        """Testa validação sem conteúdo"""
        service = DeviationClassificationService()
        request = ClassificationRequest(local="Setor 1")
        
        with pytest.raises(InvalidInputError, match="pelo menos 'description' ou 'audio'"):
            service._validate_request(request)
    
    def test_validate_request_with_valid_data(self):
        """Testa validação com dados válidos"""
        service = DeviationClassificationService()
        request = ClassificationRequest(
            local="Setor 1",
            description="Teste válido"
        )
        
        # Não deve lançar exceção
        service._validate_request(request)
