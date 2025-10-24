"""
Script para criar modelo ML mock (.pkl)
Este é um modelo de demonstração que simula um classificador treinado
"""
import pickle
import random
from typing import Dict, List

class MockDeviationClassifier:
    """
    Modelo mock que simula classificação de desvios
    Em produção, seria substituído por um modelo ML real treinado
    """
    
    def __init__(self):
        self.model_version = "1.0.0-mock"
        self.keywords = {
            'seguranca': ['perigo', 'risco', 'acidente', 'lesão', 'ferimento', 'queda', 'epi'],
            'qualidade': ['defeito', 'falha', 'problema', 'erro', 'incorreto', 'fora do padrão'],
            'ambiental': ['vazamento', 'poluição', 'resíduo', 'contaminação', 'meio ambiente'],
            'operacional': ['parada', 'atraso', 'processo', 'procedimento', 'operação'],
            'manutencao': ['quebrado', 'danificado', 'manutenção', 'reparo', 'conserto'],
            'equipamento': ['máquina', 'equipamento', 'ferramenta', 'dispositivo'],
            'comportamental': ['conduta', 'comportamento', 'atitude', 'negligência'],
        }
    
    def predict(self, text: str, location: str) -> Dict:
        """
        Prediz classificação baseado em palavras-chave
        
        Args:
            text: Texto concatenado (descrição + transcrição)
            location: Local do desvio
            
        Returns:
            Dicionário com classificação
        """
        text_lower = text.lower()
        
        # Identifica tipo baseado em keywords
        tipo = 'operacional'  # default
        max_matches = 0
        for tipo_key, keywords in self.keywords.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > max_matches:
                max_matches = matches
                tipo = tipo_key
        
        # Calcula gravidade baseado em palavras críticas
        critical_words = ['grave', 'crítico', 'urgente', 'emergência', 'perigo', 'risco alto']
        gravidade = 0.3  # base
        for word in critical_words:
            if word in text_lower:
                gravidade += 0.15
        gravidade = min(gravidade, 1.0)
        
        # Calcula urgência
        urgent_words = ['imediato', 'urgente', 'rápido', 'agora', 'emergência']
        urgencia = 0.4
        for word in urgent_words:
            if word in text_lower:
                urgencia += 0.15
        urgencia = min(urgencia, 1.0)
        
        # Tendência (probabilidade de recorrência/agravamento)
        tendencia = random.uniform(0.3, 0.7)
        
        # Determina categoria baseado em gravidade
        if gravidade >= 0.8:
            categoria = 'critico'
        elif gravidade >= 0.6:
            categoria = 'alto'
        elif gravidade >= 0.4:
            categoria = 'medio'
        elif gravidade >= 0.2:
            categoria = 'baixo'
        else:
            categoria = 'observacao'
        
        # Determina direcionamento
        direcionamento_map = {
            'seguranca': 'seguranca_trabalho',
            'ambiental': 'meio_ambiente',
            'qualidade': 'qualidade',
            'manutencao': 'manutencao',
            'equipamento': 'manutencao',
            'operacional': 'operacao',
            'comportamental': 'recursos_humanos',
        }
        
        direcionamento = direcionamento_map.get(tipo, 'gestao_instalacao')
        
        # Se gravidade crítica, sempre emergência
        if gravidade >= 0.8 and urgencia >= 0.7:
            direcionamento = 'emergencia_imediata'
        elif gravidade >= 0.6 and urgencia >= 0.6:
            direcionamento = 'supervisao_urgente'
        
        return {
            'gravidade': round(gravidade, 2),
            'urgencia': round(urgencia, 2),
            'tendencia': round(tendencia, 2),
            'tipo': tipo,
            'direcionamento': direcionamento,
            'categoria': categoria
        }

# Cria e salva o modelo
if __name__ == '__main__':
    model = MockDeviationClassifier()
    
    output_path = 'models_data/deviation_classifier.pkl'
    with open(output_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"✓ Modelo mock criado com sucesso: {output_path}")
    print(f"  Versão: {model.model_version}")
    
    # Testa o modelo
    test_text = "Identificado risco grave de queda na escada do setor 3"
    test_location = "Setor 3"
    result = model.predict(test_text, test_location)
    print(f"\n✓ Teste do modelo:")
    print(f"  Input: {test_text}")
    print(f"  Output: {result}")
