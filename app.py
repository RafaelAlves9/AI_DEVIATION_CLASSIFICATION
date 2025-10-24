
"""
Aplicação Flask para classificação de desvios
Ponto de entrada da aplicação
"""
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from app.routes.deviation_routes import register_routes
from app.utils.logger import setup_logger
from app.settings.swagger import swagger


# Carrega variáveis de ambiente
load_dotenv()

# Configura logger
logger = setup_logger('app')


def create_app() -> Flask:
    """
    Factory function para criar a aplicação Flask
    
    Returns:
        Instância configurada do Flask
    """
    # Cria app
    app = Flask(__name__)
    
    # Configurações
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max para arquivos
    app.config['JSON_AS_ASCII'] = False  # Suporta UTF-8
    
    # Configura CORS (permite qualquer origem)
    CORS(app, resources={r"/*": {"origins": "*"}})
    logger.info("CORS configurado para permitir qualquer origem")

    # Swagger UI
    swagger.init_app(app)
    logger.info("Swagger UI configurado em /docs (spec em /swagger.json)")
    
    # Registra rotas
    register_routes(app)
    
    # Cria diretório de logs se não existir
    os.makedirs('logs', exist_ok=True)
    
    logger.info("Aplicação Flask criada e configurada com sucesso")
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Configurações do servidor
    HOST = '0.0.0.0'
    PORT = 8000
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Iniciando servidor em {HOST}:{PORT} (debug={DEBUG})")
    
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG
    )
