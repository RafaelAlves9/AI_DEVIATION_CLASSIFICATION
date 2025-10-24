
"""
Rotas/Controllers para classificação de desvios
Define os endpoints da API
"""
import base64
from flask import Blueprint, request, jsonify
from app.services.deviation_classification_service import DeviationClassificationService
from app.services.transcription_service import TranscriptionService
from app.services.ml_model_service import MLModelService
from app.services.ai_validation_service import AIValidationService
from app.models.schemas import (
    ClassificationRequest, DeviationClassification
)
from app.utils.exceptions import DeviationClassifierError
from app.utils.logger import setup_logger


logger = setup_logger(__name__)

# Cria blueprint para as rotas
deviation_bp = Blueprint('deviation', __name__)

# Inicializa serviços (singletons para performance)
classification_service = DeviationClassificationService()
transcription_service = TranscriptionService()
ml_service = MLModelService()
ai_service = AIValidationService()


@deviation_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de health check

    ---
    tags:
      - Health
    summary: Verifica saúde da aplicação
    produces:
      - application/json
    responses:
      200:
        description: Status da aplicação e serviços
      503:
        description: Serviço degradado ou indisponível
    """
    try:
        services_status = classification_service.health_check()
        
        # Determina status geral
        all_healthy = all(services_status.values())
        
        return jsonify({
            'status': 'healthy' if all_healthy else 'degraded',
            'services': services_status
        }), 200 if all_healthy else 503
        
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


@deviation_bp.route('/api/classify-deviation', methods=['POST'])
def classify_deviation():
    """
    Endpoint para classificação de desvios

    ---
    tags:
      - Deviation
    summary: Classifica um desvio a partir de texto e/ou áudio
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: local
        type: string
        required: false
        description: Local do desvio
      - in: formData
        name: description
        type: string
        required: false
        description: Descrição textual do desvio
      - in: formData
        name: audio
        type: file
        required: false
        description: Arquivo MP3 com áudio do desvio
    produces:
      - application/json
    responses:
      200:
        description: Classificação realizada com sucesso
      400:
        description: Erro de entrada inválida
      500:
        description: Erro interno do servidor
    """
    try:
        # Processa requisição (suporta JSON e multipart)
        local = None
        description = None
        audio = None
        
        # Tenta obter dados de JSON
        if request.is_json:
            data = request.get_json()
            local = data.get('local')
            description = data.get('description')
            audio_base64 = data.get('audio')
            
            # Decodifica áudio se fornecido em base64
            if audio_base64:
                try:
                    audio = base64.b64decode(audio_base64)
                except Exception as e:
                    logger.error(f"Erro ao decodificar áudio base64: {str(e)}")
                    return jsonify({
                        'error': 'InvalidInput',
                        'message': 'Áudio base64 inválido',
                        'details': {'error': str(e)}
                    }), 400
        
        # Tenta obter dados de form-data
        else:
            local = request.form.get('local')
            description = request.form.get('description')
            
            # Tenta obter arquivo de áudio
            if 'audio' in request.files:
                audio_file = request.files['audio']
                if audio_file.filename:
                    audio = audio_file.read()
        
        # Cria objeto de requisição
        classification_request = ClassificationRequest(
            local=local,
            description=description,
            audio=audio
        )
        
        logger.info(f"Recebida requisição de classificação: local='{local}'")
        
        # Processa classificação
        result = classification_service.classify(classification_request)
        
        # Retorna resultado
        return jsonify(result.to_dict()), 200
        
    except DeviationClassifierError as e:
        # Erros conhecidos da aplicação
        logger.warning(f"Erro de aplicação: {e.message}")
        return jsonify(e.to_dict()), 400
        
    except Exception as e:
        # Erros inesperados
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'InternalServerError',
            'message': 'Erro interno do servidor',
            'details': {'error': str(e)}
        }), 500


@deviation_bp.route('/api/transcribe-audio', methods=['POST'])
def transcribe_audio():
    """
    Transcreve um arquivo de áudio para texto

    ---
    tags:
      - Deviation
    summary: Transcreve áudio usando Faster-Whisper
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: audio
        type: file
        required: true
        description: Arquivo MP3/WAV com áudio para transcrição
    produces:
      - application/json
    responses:
      200:
        description: Texto transcrito
      400:
        description: Entrada inválida
      500:
        description: Erro interno do servidor
    """
    try:
        if 'audio' not in request.files or not request.files['audio'].filename:
            return jsonify({
                'error': 'InvalidInput',
                'message': "Arquivo 'audio' é obrigatório"
            }), 400

        audio_file = request.files['audio']
        audio_bytes = audio_file.read()

        text = transcription_service.transcribe(audio_bytes)
        return jsonify({'text': text}), 200
    except DeviationClassifierError as e:
        logger.warning(f"Erro de aplicação: {e.message}")
        return jsonify(e.to_dict()), 400
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'InternalServerError',
            'message': 'Erro interno do servidor',
            'details': {'error': str(e)}
        }), 500


@deviation_bp.route('/api/ml-classify', methods=['POST'])
def ml_classify():
    """
    Classifica um desvio apenas com o modelo ML

    ---
    tags:
      - Deviation
    summary: Classificação via modelo ML (sem IA)
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: local
        type: string
        required: true
        description: Local do desvio
      - in: formData
        name: description
        type: string
        required: true
        description: Descrição textual do desvio
    produces:
      - application/json
    responses:
      200:
        description: Classificação do modelo ML
      400:
        description: Entrada inválida
      500:
        description: Erro interno do servidor
    """
    try:
        local = request.form.get('local')
        description = request.form.get('description')
        if not local or not description:
            return jsonify({
                'error': 'InvalidInput',
                'message': "'local' e 'description' são obrigatórios"
            }), 400

        classification = ml_service.classify(description, local)
        return jsonify(classification.to_dict()), 200
    except DeviationClassifierError as e:
        logger.warning(f"Erro de aplicação: {e.message}")
        return jsonify(e.to_dict()), 400
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'InternalServerError',
            'message': 'Erro interno do servidor',
            'details': {'error': str(e)}
        }), 500


@deviation_bp.route('/api/ai-validate', methods=['POST'])
def ai_validate():
    """
    Valida/corrige uma classificação usando IA (Abacus)

    ---
    tags:
      - Deviation
    summary: Validação via IA Abacus com JSON de classificação
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: AIValidationRequest
          type: object
          properties:
            local:
              type: string
              description: "Local onde o desvio ocorreu."
              example: "Área de Montagem"
            text:
              type: string
              description: "Descrição completa do desvio (pode incluir transcrição de áudio)."
              example: "Operador utilizando a furadeira sem óculos de proteção."
            classification:
              type: object
              description: "Objeto com a classificação gerada pelo modelo de ML."
              properties:
                gravidade:
                  type: integer
                  example: 3
                urgencia:
                  type: integer
                  example: 4
                tendencia:
                  type: integer
                  example: 3
                tipo:
                  type: integer
                  example: 1
                direcionamento:
                  type: integer
                  example: 2
                categoria:
                  type: integer
                  example: 1
          required:
            - local
            - text
            - classification
    produces:
      - application/json
    responses:
      200:
        description: Classificação validada/corrigida
      400:
        description: Entrada inválida
      500:
        description: Erro interno do servidor
    """
    try:
        if not request.is_json:
            return jsonify({
                'error': 'InvalidInput',
                'message': 'Content-Type application/json é obrigatório'
            }), 400
        data = request.get_json() or {}
        local = data.get('local')
        text = data.get('text')
        classification_data = data.get('classification')
        if not local or not text or not classification_data:
            return jsonify({
                'error': 'InvalidInput',
                'message': "Campos 'local', 'text' e 'classification' são obrigatórios"
            }), 400

        # Monta objeto DeviationClassification a partir do JSON flat
        classification = DeviationClassification(**classification_data)

        validated = ai_service.validate_and_correct(text, local, classification)
        return jsonify(validated.to_dict()), 200
    except (DeviationClassifierError, TypeError, KeyError) as e:
        logger.warning(f"Erro de aplicação ou dados inválidos: {str(e)}")
        error_dict = e.to_dict() if hasattr(e, 'to_dict') else {
            'error': 'InvalidInput', 'message': str(e)
        }
        return jsonify(error_dict), 400
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'InternalServerError',
            'message': 'Erro interno do servidor',
            'details': {'error': str(e)}
        }), 500


def register_routes(app):
    """
    Registra as rotas no app Flask
    
    Args:
        app: Instância do Flask
    """
    app.register_blueprint(deviation_bp)
    logger.info("Rotas registradas com sucesso")
