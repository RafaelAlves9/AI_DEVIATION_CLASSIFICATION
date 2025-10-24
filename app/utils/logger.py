
"""
Configuração de logging para a aplicação
"""
import logging
import sys
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = 'deviation_classifier') -> logging.Logger:
    """
    Configura e retorna um logger
    
    Args:
        name: Nome do logger
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evita duplicação de handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Formato de log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo (rotativo)
    try:
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        # Se não conseguir criar arquivo de log, apenas usa console
        pass
    
    return logger
