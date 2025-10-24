from flasgger import Swagger


swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "AI Deviation Classification API",
        "description": "API para classificação de desvios e transcrição de áudio.",
        "version": "1.0.0",
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "ApiKeyAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        }
    },
    "tags": [
        {"name": "Deviation", "description": "Endpoints de classificação"},
        {"name": "Health", "description": "Healthcheck"},
    ],
}


swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/swagger.json",
            "rule_filter": lambda rule: True,  # documenta todas as rotas
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/",
}


# Expor como variável para manter o padrão de importação requerido
# Usage: from app.settings.swagger import swagger
swagger = Swagger(template=swagger_template, config=swagger_config)


