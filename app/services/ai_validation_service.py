"""
Serviço de validação com IA usando Abacus.AI
Responsável por validar e corrigir classificações usando LLM
"""
import os
import json
from typing import Dict, Optional
import requests
from app.utils.exceptions import AIValidationError
from app.utils.logger import setup_logger
from app.models.schemas import DeviationClassification
from app.models.enums import (
    DeviationType, DeviationCategory, DeviationDirectioning,
    GravityLevel, UrgencyLevel, TrendLevel
)


logger = setup_logger(__name__)


class AIValidationService:
    """
    Serviço para validação de classificação usando IA (Abacus.AI)
    
    Principles:
    - Single Responsibility: Apenas validação/correção com IA
    - Dependency Injection: Cliente HTTP pode ser injetado futuramente
    - Interface Segregation: Expõe apenas métodos necessários
    """
    
    SYSTEM_PROMPT = """Você é um agente de segurança experiente em uma empresa industrial.
Sua função é analisar desvios e incidentes reportados, garantindo que a classificação esteja coerente e precisa.

Você deve validar e, se necessário, corrigir a classificação de desvios baseado em:
- `gravidade`: Severidade do problema (0-5)
- `urgencia`: Necessidade de resposta rápida (0-5)
- `tendencia`: Probabilidade de recorrência ou agravamento (0-5)
- `tipo`: Categoria do desvio (0-2)
- `direcionamento`: Área/equipe responsável pelo tratamento (0-4)
- `categoria`: Categoria específica do desvio (0-12)

Valores de 'gravidade' (int): 0=NotDefined, 1=NoGravity, 2=LowGravity, 3=MediumGravity, 4=HighGravity, 5=ExtremeGravity
Valores de 'urgencia' (int): 0=NotDefined, 1=CanWait, 2=NotVeryUrgent, 3=AsSoonAsPossible, 4=Urgent, 5=NeedsImmediateAction
Valores de 'tendencia' (int): 0=NotDefined, 1=NoTrend, 2=WillGetWorseInTheLongTerm, 3=WillGetWorse, 4=WillGetWorseInTheShortTerm, 5=WillGetWorseQuickly
Valores de 'tipo' (int): 0=NotDefined, 1=Behavior, 2=Structure
Valores de 'direcionamento' (int): 0=NotDefined, 1=Factory, 2=Unit, 3=Facilities, 4=EnvironmentAndQuality
Valores de 'categoria' (int): 0=NotDefined, 1=EpiOrEpc, 2=Bos, 3=OrderAndCleanlinessFiveS, 4=Equipment, 5=Ergonomics, 6=TrafficOfVehiclesAndPeople, 7=Environment, 8=Quality, 9=WorkRulesProceduresAndInstructions, 10=MobileEquipment, 11=ToolsAndEquipment, 12=Other

Analise a descrição do desvio e a classificação fornecida. Se estiver coerente, retorne a mesma classificação.
Se houver incoerências, corrija e retorne a versão corrigida.

IMPORTANTE: Retorne APENAS um objeto JSON válido, sem texto adicional, com a estrutura flat (plana):
{
    "gravidade": <int>, "urgencia": <int>, "tendencia": <int>,
    "tipo": <int>, "direcionamento": <int>, "categoria": <int>
}"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Inicializa o serviço de validação com IA
        
        Args:
            api_key: Chave API do Abacus.AI (se None, lê de variável de ambiente)
            base_url: URL base do roteador LLM (default Abacus)
        """
        logger.info("IAValidationService inicializado")
        self.api_key =  "s2_152d8a05011b40ea9dc8f35608a15748"
        self.base_url = (base_url or "https://routellm.abacus.ai/v1").rstrip("/")
        
        if not self.api_key:
            logger.warning("IA desabilitada: defina ABACUS_API_KEY")
        else:
            logger.info("IA pronta (Abacus.AI)")
    
    def _request_chat_completion(self, messages: list, temperature: float, max_tokens: int) -> Optional[str]:
        """Faz a requisição HTTP ao endpoint compatível de chat completions."""
        if not self.api_key:
            return None
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "auto",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code != 200:
                logger.error(f"IA HTTP {response.status_code}")
                return None
            data = response.json()
            # Estrutura OpenAI-compatível
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"IA request falhou: {str(e)}")
            return None
    
    def validate_and_correct(
        self,
        text: str,
        location: str,
        classification: DeviationClassification
    ) -> DeviationClassification:
        """
        Valida classificação com IA e corrige se necessário
        
        Args:
            text: Texto do desvio (descrição + transcrição)
            location: Local do desvio
            classification: Classificação inicial do modelo ML
            
        Returns:
            DeviationClassification validada/corrigida
            
        Raises:
            AIValidationError: Se houver erro na validação
        """
        if not self.api_key:
            logger.warning("IA indisponível (sem chave) - mantendo ML")
            return classification
        
        try:
            logger.info(f"IA validar: local={location}")
            
            # Prepara prompt do usuário
            user_prompt = self._build_user_prompt(text, location, classification)
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
            
            ai_response = self._request_chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            if not ai_response:
                logger.warning("IA sem resposta - mantendo ML")
                return classification
            logger.debug(f"IA resposta={ai_response}")
            
            # Parse da resposta JSON flat
            corrected_data = self._parse_ai_response(ai_response)
            
            # Cria nova classificação com dados corrigidos
            corrected_classification = DeviationClassification(**corrected_data)
            
            # Log se houve correção
            if corrected_classification.to_dict() != classification.to_dict():
                logger.info("IA corrigiu classificação")
                logger.debug(f"ML={classification.to_dict()}")
                logger.debug(f"IA={corrected_classification.to_dict()}")
            else:
                logger.info("IA validou classificação (sem mudanças)")
            
            return corrected_classification
            
        except AIValidationError:
            raise
        except Exception as e:
            logger.error(f"IA erro: {str(e)}")
            logger.warning("Mantendo classificação ML")
            return classification
    
    def _build_user_prompt(
        self,
        text: str,
        location: str,
        classification: DeviationClassification
    ) -> str:
        """
        Constrói prompt do usuário para a IA
        
        Args:
            text: Texto do desvio
            location: Local
            classification: Classificação inicial
            
        Returns:
            Prompt formatado
        """
        current_classification_json = json.dumps(classification.to_dict(), indent=4)
        
        prompt = f"""Desvio reportado:
Local: {location}
Descrição: {text}

Classificação atual:
{current_classification_json}

Valide esta classificação e retorne em formato JSON flat:
{{
    "gravidade": <int>,
    "urgencia": <int>,
    "tendencia": <int>,
    "tipo": <int>,
    "direcionamento": <int>,
    "categoria": <int>
}}"""
        
        return prompt
    
    def _parse_ai_response(self, response: str) -> Dict:
        """
        Faz parse da resposta da IA
        
        Args:
            response: Resposta em texto da IA
            
        Returns:
            Dicionário com classificação
            
        Raises:
            AIValidationError: Se não conseguir fazer parse
        """
        try:
            # Tenta extrair JSON da resposta
            # Remove markdown code blocks se houver
            response = response.strip()
            if response.startswith('```'):
                response = response.split('```')[1]
                if response.startswith('json'):
                    response = response[4:]
                response = response.strip()
            
            data = json.loads(response)
            
            # Valida campos obrigatórios
            required_fields = ['gravidade', 'urgencia', 'tendencia', 'tipo', 'direcionamento', 'categoria']
            for field in required_fields:
                if field not in data:
                    raise AIValidationError(
                        f"Campo obrigatório ausente na resposta da IA: {field}",
                        details={'response': response}
                    )
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON da IA: {str(e)}")
            raise AIValidationError(
                "Resposta da IA não está em formato JSON válido",
                details={'response': response, 'error': str(e)}
            )
    
    def is_available(self) -> bool:
        """
        Verifica se o serviço de validação está disponível
        
        Returns:
            True se disponível, False caso contrário
        """
        return bool(self.api_key)
