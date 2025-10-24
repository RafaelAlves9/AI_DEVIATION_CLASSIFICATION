"""
Script para criar modelo ML mock (.pkl)
Este é um modelo de demonstração que simula um classificador treinado
"""
import pickle
import random
from typing import Dict, List

# Importa os enums para usar os valores diretamente
from app.models.enums import (
    GravityLevel, UrgencyLevel, TrendLevel,
    DeviationType, DeviationDirectioning, DeviationCategory
)

def _map_score_to_gravity(score: float) -> int:
    if score >= 0.8: return GravityLevel.ExtremeGravity.value
    if score >= 0.6: return GravityLevel.HighGravity.value
    if score >= 0.4: return GravityLevel.MediumGravity.value
    if score >= 0.2: return GravityLevel.LowGravity.value
    if score > 0.0: return GravityLevel.NoGravity.value
    return GravityLevel.NotDefined.value

def _map_score_to_urgency(score: float) -> int:
    if score >= 0.8: return UrgencyLevel.NeedsImmediateAction.value
    if score >= 0.6: return UrgencyLevel.Urgent.value
    if score >= 0.4: return UrgencyLevel.AsSoonAsPossible.value
    if score >= 0.2: return UrgencyLevel.NotVeryUrgent.value
    if score > 0.0: return UrgencyLevel.CanWait.value
    return UrgencyLevel.NotDefined.value

def _map_score_to_trend(score: float) -> int:
    if score >= 0.8: return TrendLevel.WillGetWorseQuickly.value
    if score >= 0.6: return TrendLevel.WillGetWorseInTheShortTerm.value
    if score >= 0.4: return TrendLevel.WillGetWorse.value
    if score >= 0.2: return TrendLevel.WillGetWorseInTheLongTerm.value
    if score > 0.0: return TrendLevel.NoTrend.value
    return TrendLevel.NotDefined.value


class MockDeviationClassifier:
    """
    Modelo mock que simula classificação de desvios
    Em produção, seria substituído por um modelo ML real treinado
    """
    
    def __init__(self):
        self.model_version = "1.0.0-mock"
        self.keywords = {
            # Mapeia para categorias para simular uma lógica
            'EpiOrEpc': ['perigo', 'risco', 'acidente', 'lesão', 'ferimento', 'queda', 'epi'],
            'Quality': ['defeito', 'falha', 'problema', 'erro', 'incorreto', 'fora do padrão'],
            'Environment': ['vazamento', 'poluição', 'resíduo', 'contaminação', 'meio ambiente'],
            'Equipment': ['máquina', 'equipamento', 'ferramenta', 'dispositivo', 'quebrado', 'danificado'],
            'WorkRulesProceduresAndInstructions': ['processo', 'procedimento', 'operação', 'regra'],
            'Behavior': ['conduta', 'comportamento', 'atitude', 'negligência', 'imprudência']
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
        
        # Identifica categoria baseado em keywords
        categoria = DeviationCategory.Other.value  # default
        max_matches = 0
        for cat_key, keywords in self.keywords.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > max_matches:
                max_matches = matches
                categoria = DeviationCategory[cat_key].value
        
        # Calcula gravidade baseado em palavras críticas
        critical_words = ['grave', 'crítico', 'urgente', 'emergência', 'perigo', 'risco alto']
        gravidade_score = 0.3  # base
        for word in critical_words:
            if word in text_lower:
                gravidade_score += 0.15
        gravidade_score = min(gravidade_score, 1.0)
        
        # Calcula urgência
        urgent_words = ['imediato', 'urgente', 'rápido', 'agora', 'emergência']
        urgencia_score = 0.4
        for word in urgent_words:
            if word in text_lower:
                urgencia_score += 0.15
        urgencia_score = min(urgencia_score, 1.0)
        
        # Tendência (probabilidade de recorrência/agravamento)
        tendencia_score = random.uniform(0.3, 0.7)
        
        # Determina tipo (simples)
        tipo = DeviationType.Behavior.value if 'comportamento' in text_lower or 'atitude' in text_lower else DeviationType.Structure.value
        
        # Determina direcionamento
        direcionamento_map = {  # Simula um direcionamento básico
            'EpiOrEpc': DeviationDirectioning.Unit.value,
            'Environment': DeviationDirectioning.EnvironmentAndQuality.value,
            'Quality': DeviationDirectioning.EnvironmentAndQuality.value,
            'Equipment': DeviationDirectioning.Facilities.value,
            'Behavior': DeviationDirectioning.Factory.value,
        }
        
        # A lógica para encontrar a chave correspondente à categoria precisa ser ajustada
        categoria_str = DeviationCategory(categoria).name
        direcionamento = direcionamento_map.get(categoria_str, DeviationDirectioning.Factory.value)
        
        return {
            'gravidade': _map_score_to_gravity(gravidade_score),
            'urgencia': _map_score_to_urgency(urgencia_score),
            'tendencia': _map_score_to_trend(tendencia_score),
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
