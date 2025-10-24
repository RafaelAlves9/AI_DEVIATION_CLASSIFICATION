
"""
Rotas/Controllers para classificação de desvios
Define os endpoints da API
"""
import base64
from flask import Blueprint, request, jsonify
from app.services.deviation_classification_service import DeviationClassificationService
from app.models.schemas import ClassificationRequest
from app.utils.exceptions import DeviationClassifierError
from app.utils.logger import setup_logger


logger = setup_logger(__name__)

# Cria blueprint para as rotas
deviation_bp = Blueprint('deviation', __name__)

# Inicializa serviço (singleton para performance)
classification_service = DeviationClassificationService()


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
      - application/json
      - multipart/form-data
    parameters:
      - in: body
        name: body
        required: false
        schema:
          type: object
          properties:
            local:
              type: string
              description: Local do desvio
            description:
              type: string
              description: Descrição textual do desvio
            audio:
              type: string
              description: Áudio em base64
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


def register_routes(app):
    """
    Registra as rotas no app Flask
    
    Args:
        app: Instância do Flask
    """
    app.register_blueprint(deviation_bp)
    logger.info("Rotas registradas com sucesso")
