
"""
Fixtures compartilhadas para testes
"""
import pytest
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def sample_audio_bytes():
    """Retorna bytes de áudio de exemplo (fake)"""
    # Em testes reais, seria um arquivo MP3 real
    return b'\xff\xfb\x90\x00' * 1000  # Fake MP3 header + data


@pytest.fixture
def sample_classification_data():
    """Retorna dados de classificação de exemplo"""
    return {
        'gravidade': 0.6,
        'urgencia': 0.5,
        'tendencia': 0.4,
        'tipo': 'seguranca',
        'direcionamento': 'seguranca_trabalho',
        'categoria': 'medio'
    }


@pytest.fixture
def sample_request_data():
    """Retorna dados de requisição de exemplo"""
    return {
        'local': 'Setor 3',
        'description': 'Equipamento danificado',
        'audio': None
    }
