
"""
Testes para rotas/endpoints da API
"""
import pytest
import json
import base64
from app import create_app


@pytest.fixture
def client():
    """Cria cliente de teste do Flask"""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Testes para endpoint /health"""
    
    def test_health_check_success(self, client):
        """Testa health check com sucesso"""
        response = client.get('/health')
        
        assert response.status_code in [200, 503]
        data = json.loads(response.data)
        assert 'status' in data
        assert 'services' in data


class TestClassifyDeviationEndpoint:
    """Testes para endpoint /api/classify-deviation"""
    
    def test_classify_with_description_json(self, client):
        """Testa classificação com descrição via JSON"""
        payload = {
            'local': 'Setor 3',
            'description': 'Equipamento danificado com risco de acidente'
        }
        
        response = client.post(
            '/api/classify-deviation',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'gravidade' in data
        assert 'urgencia' in data
        assert 'tipo' in data
        assert 'categoria' in data
    
    def test_classify_without_local(self, client):
        """Testa classificação sem local"""
        payload = {
            'description': 'Teste sem local'
        }
        
        response = client.post(
            '/api/classify-deviation',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_classify_without_content(self, client):
        """Testa classificação sem descrição nem áudio"""
        payload = {
            'local': 'Setor 1'
        }
        
        response = client.post(
            '/api/classify-deviation',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_classify_with_audio_base64(self, client):
        """Testa classificação com áudio em base64"""
        fake_audio = b'\xff\xfb\x90\x00' * 100
        audio_base64 = base64.b64encode(fake_audio).decode('utf-8')
        
        payload = {
            'local': 'Setor 2',
            'audio': audio_base64
        }
        
        response = client.post(
            '/api/classify-deviation',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Pode falhar na transcrição (esperado com fake audio)
        # mas não deve dar erro 500
        assert response.status_code in [200, 400]
