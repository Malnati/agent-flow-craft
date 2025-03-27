# Sistema de logging centralizado com suporte a múltiplos níveis e saídas
import os
import sys
import logging
import logging.handlers
from pathlib import Path
from functools import wraps
import time
import traceback

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Garantir que o diretório de logs existe
os.makedirs(LOG_DIR, exist_ok=True)

# Configuração de níveis de log
LOG_LEVEL_MAP = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# Nível de log padrão - pode ser sobrescrito via variável de ambiente
DEFAULT_LOG_LEVEL = 'INFO'
LOG_LEVEL = os.environ.get('LOG_LEVEL', DEFAULT_LOG_LEVEL).upper()
NUMERIC_LOG_LEVEL = LOG_LEVEL_MAP.get(LOG_LEVEL, logging.INFO)

# Formato padrão para os logs
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Cores para logs no console
COLORS = {
    'DEBUG': '\033[94m',  # Azul
    'INFO': '\033[92m',   # Verde
    'WARNING': '\033[93m', # Amarelo
    'ERROR': '\033[91m',  # Vermelho
    'CRITICAL': '\033[1;91m', # Vermelho brilhante
    'RESET': '\033[0m'    # Resetar cor
}

class ColoredFormatter(logging.Formatter):
    """Formatador personalizado que adiciona cores aos logs no console."""
    
    def format(self, record):
        levelname = record.levelname
        # Adicionar cores apenas para terminal interativo
        if sys.stdout.isatty():
            colored_levelname = f"{COLORS.get(levelname, '')}{levelname}{COLORS['RESET']}"
            record.levelname = colored_levelname
        result = super().format(record)
        # Restaurar levelname original
        record.levelname = levelname
        return result

def setup_logging(logger_name=None, log_file=None):
    """
    Configura o sistema de logging com handlers para console e arquivo.
    
    Args:
        logger_name (str): Nome do logger (se None, usa o logger raiz)
        log_file (str): Nome do arquivo de log (se None, usa um nome baseado na data)
        
    Returns:
        logging.Logger: O logger configurado
    """
    # Se não especificado um nome para o arquivo de log, usar timestamp
    if log_file is None:
        timestamp = time.strftime("%Y%m%d")
        log_file = f"application_{timestamp}.log" 
    
    log_path = os.path.join(LOG_DIR, log_file)
    
    # Obter ou criar logger
    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger()
        
    # Redefine handlers se o logger já existir
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Configurar nível de log
    logger.setLevel(NUMERIC_LOG_LEVEL)
    
    # Criar formatador padrão
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # Handler para console com cores
    console_handler = logging.StreamHandler()
    console_handler.setLevel(NUMERIC_LOG_LEVEL)
    colored_formatter = ColoredFormatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo com rotação
    file_handler = logging.handlers.RotatingFileHandler(
        log_path, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=7  # 7 arquivos de backup
    )
    file_handler.setLevel(NUMERIC_LOG_LEVEL)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def get_logger(name=None):
    """
    Obtém um logger configurado.
    Se o logger já existe, retorna-o. Caso contrário, configura um novo.
    
    Args:
        name (str): Nome do logger (geralmente __name__)
        
    Returns:
        logging.Logger: O logger configurado
    """
    logger = logging.getLogger(name or __name__)
    
    # Se o logger raiz não estiver configurado, configura-o
    if not logging.getLogger().handlers:
        setup_logging()
        
    return logger

def log_execution(func=None, level=logging.INFO):
    """
    Decorador para logar a entrada e saída de funções.
    
    Args:
        func: A função a ser decorada
        level: Nível de log (padrão: INFO)
        
    Returns:
        Função decorada
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            
            # Limpar argumentos sensíveis (senhas, tokens)
            safe_kwargs = {
                k: '***' if any(s in k.lower() for s in ['pass', 'token', 'secret', 'key']) 
                else v for k, v in kwargs.items()
            }
            
            func_name = func.__qualname__
            logger.log(level, f"Iniciando {func_name} - Args: {args}, Kwargs: {safe_kwargs}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.log(level, f"Concluído {func_name} em {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Erro em {func_name} após {elapsed:.3f}s: {str(e)}", 
                             exc_info=True)
                raise
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)

# Configuração inicial do logger raiz
root_logger = setup_logging()
root_logger.debug(f"Sistema de logging inicializado - Nível: {LOG_LEVEL}")
