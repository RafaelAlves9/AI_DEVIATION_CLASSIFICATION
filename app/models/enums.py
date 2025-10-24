
"""
Enums para classificação de desvios
Define todos os valores possíveis para tipos, categorias e direcionamentos
"""
from enum import IntEnum


class GravityLevel(IntEnum):
    """Níveis de Gravidade"""
    NotDefined = 0
    NoGravity = 1
    LowGravity = 2
    MediumGravity = 3
    HighGravity = 4
    ExtremeGravity = 5


class UrgencyLevel(IntEnum):
    """Níveis de Urgência"""
    NotDefined = 0
    CanWait = 1
    NotVeryUrgent = 2
    AsSoonAsPossible = 3
    Urgent = 4
    NeedsImmediateAction = 5


class TrendLevel(IntEnum):
    """Níveis de Tendência"""
    NotDefined = 0
    NoTrend = 1
    WillGetWorseInTheLongTerm = 2
    WillGetWorse = 3
    WillGetWorseInTheShortTerm = 4
    WillGetWorseQuickly = 5


class DeviationType(IntEnum):
    """Tipos de desvio"""
    NotDefined = 0
    Behavior = 1
    Structure = 2


class DeviationDirectioning(IntEnum):
    """Direcionamentos para tratamento"""
    NotDefined = 0
    Factory = 1
    Unit = 2
    Facilities = 3
    EnvironmentAndQuality = 4


class DeviationCategory(IntEnum):
    """Categorias do desvio"""
    NotDefined = 0
    EpiOrEpc = 1
    Bos = 2
    OrderAndCleanlinessFiveS = 3
    Equipment = 4
    Ergonomics = 5
    TrafficOfVehiclesAndPeople = 6
    Environment = 7
    Quality = 8
    WorkRulesProceduresAndInstructions = 9
    MobileEquipment = 10
    ToolsAndEquipment = 11
    Other = 12
