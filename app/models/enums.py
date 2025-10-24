
"""
Enums para classificação de desvios
Define todos os valores possíveis para tipos, categorias e direcionamentos
"""
from enum import Enum


class DeviationType(str, Enum):
    """Tipos de desvio possíveis"""
    SEGURANCA = "seguranca"
    QUALIDADE = "qualidade"
    AMBIENTAL = "ambiental"
    OPERACIONAL = "operacional"
    MANUTENCAO = "manutencao"
    EQUIPAMENTO = "equipamento"
    PROCEDIMENTO = "procedimento"
    COMPORTAMENTAL = "comportamental"
    DOCUMENTACAO = "documentacao"
    INFRAESTRUTURA = "infraestrutura"


class DeviationCategory(str, Enum):
    """Categorias de classificação do desvio"""
    CRITICO = "critico"
    ALTO = "alto"
    MEDIO = "medio"
    BAIXO = "baixo"
    OBSERVACAO = "observacao"


class DeviationDirectioning(str, Enum):
    """Direcionamentos possíveis para tratamento do desvio"""
    EMERGENCIA_IMEDIATA = "emergencia_imediata"
    SUPERVISAO_URGENTE = "supervisao_urgente"
    MANUTENCAO = "manutencao"
    ENGENHARIA = "engenharia"
    QUALIDADE = "qualidade"
    SEGURANCA_TRABALHO = "seguranca_trabalho"
    MEIO_AMBIENTE = "meio_ambiente"
    RECURSOS_HUMANOS = "recursos_humanos"
    OPERACAO = "operacao"
    GESTAO_INSTALACAO = "gestao_instalacao"
    DOCUMENTACAO_APENAS = "documentacao_apenas"
