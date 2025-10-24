
"""
Testes para MLModelService
"""
import pytest
from app.services.ml_model_service import MLModelService
from app.utils.exceptions import MLModelError


class TestMLModelService:
    """Testes para MLModelService"""
    
    def test_model_loading(self):
        """Testa carregamento do modelo"""
        service = MLModelService()
        assert service.model is not None
        assert hasattr(service.model, 'predict')
    
    def test_is_available(self):
        """Testa verificação de disponibilidade"""
        service = MLModelService()
        assert service.is_available() is True
    
    def test_classify_with_valid_input(self):
        """Testa classificação com entrada válida"""
        service = MLModelService()
        result = service.classify(
            text="Equipamento com defeito grave",
            location="Setor 2"
        )
        
        assert result is not None
        assert 0.0 <= result.gravidade <= 1.0
        assert 0.0 <= result.urgencia <= 1.0
        assert 0.0 <= result.tendencia <= 1.0
        assert result.tipo is not None
    
    def test_classify_with_empty_text(self):
        """Testa classificação com texto vazio"""
        service = MLModelService()
        
        with pytest.raises(MLModelError, match="Texto vazio"):
            service.classify(text="", location="Setor 1")
    
    def test_classify_with_empty_location(self):
        """Testa classificação com local vazio"""
        service = MLModelService()
        
        with pytest.raises(MLModelError, match="Local não fornecido"):
            service.classify(text="Teste", location="")
    
    def test_model_invalid_path(self):
        """Testa carregamento com caminho inválido"""
        service = MLModelService(model_path="invalid/path.pkl")
        
        with pytest.raises(MLModelError):
            _ = service.model
