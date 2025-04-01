# Sistema de logging centralizado com suporte a múltiplos níveis e saídas
import os
import sys
import logging
import logging.handlers
from pathlib import Path
from functools import wraps
import time
import traceback
import re

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

# Lista de palavras-chave para identificar dados sensíveis
SENSITIVE_KEYWORDS = [
    'pass', 'senha', 'password', 
    'token', 'access_token', 'refresh_token', 'jwt', 
    'secret', 'api_key', 'apikey', 'key', 
    'auth', 'credential', 'oauth', 
    'private', 'signature'
]

# Padrões de tokens a serem mascarados
TOKEN_PATTERNS = [
    # OpenAI tokens
    r'sk-[a-zA-Z0-9]{20,}',
    r'sk-proj-[a-zA-Z0-9_-]{20,}',
    # GitHub tokens
    r'gh[pous]_[a-zA-Z0-9]{20,}',
    r'github_pat_[a-zA-Z0-9]{20,}',
    # JWT tokens
    r'eyJ[a-zA-Z0-9_-]{5,}\.eyJ[a-zA-Z0-9_-]{5,}\.[a-zA-Z0-9_-]{5,}',
    # Tokens genéricos (sequências longas de caracteres)
    r'[a-zA-Z0-9_-]{30,}'
]

def mask_sensitive_data(data, mask_str='***'):
    """
    Mascara dados sensíveis em strings e dicionários.
    
    Args:
        data: Dados a serem mascarados (string, dict ou outro tipo)
        mask_str: String de substituição para dados sensíveis
        
    Returns:
        Dados com informações sensíveis mascaradas
    """
    if isinstance(data, dict):
        # Mascara valores em dicionários
        return {
            k: mask_str if any(keyword in k.lower() for keyword in SENSITIVE_KEYWORDS) else 
               mask_sensitive_data(v, mask_str) if isinstance(v, (dict, str)) else v 
            for k, v in data.items()
        }
    elif isinstance(data, str):
        # Máscara imediata para strings muito longas (potencialmente tokens)
        if len(data) > 20 and any(keyword in data.lower() for keyword in SENSITIVE_KEYWORDS):
            # Se contém palavras-chave sensíveis e é longo, mascarar completamente
            return mask_partially(data, mask_str)
            
        # Mascara padrões em strings (ex: chaves de API, tokens)
        masked_data = data
        for pattern in TOKEN_PATTERNS:
            # Só aplicar regex em strings com comprimento suficiente (evita operações caras)
            if len(masked_data) > 20 and re.search(pattern, masked_data):
                # Mascarar parcialmente mantendo começo e fim
                masked_data = re.sub(pattern, lambda m: mask_partially(m.group(0), mask_str), masked_data)
        
        return masked_data
    else:
        # Retorna o valor original para outros tipos
        return data

def mask_partially(text, mask_str='***'):
    """Mascara parcialmente uma string, deixando alguns caracteres iniciais e finais visíveis"""
    if len(text) <= 10:
        return mask_str
    
    # Preservar parte inicial e final
    prefix_len = min(4, len(text) // 4)
    suffix_len = min(4, len(text) // 4)
    
    prefix = text[:prefix_len] 
    suffix = text[-suffix_len:] if suffix_len > 0 else ""
    
    return f"{prefix}{mask_str}{suffix}"

class ColoredFormatter(logging.Formatter):
    """Formatador personalizado que adiciona cores aos logs no console."""
    
    def format(self, record):
        levelname = record.levelname
        # Adicionar cores apenas para terminal interativo
        if sys.stdout.isatty():
            colored_levelname = f"{COLORS.get(levelname, '')}{levelname}{COLORS['RESET']}"
            record.levelname = colored_levelname
        
        # Mascarar dados sensíveis no registro antes de formatar
        if isinstance(record.msg, str):
            record.msg = mask_sensitive_data(record.msg)
        
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
            
            # Verificação e mascaramento mais agressivo para argumentos
            safe_args = []
            for arg in args:
                if isinstance(arg, str):
                    # Verificar se é potencialmente um token ou valor sensível
                    if len(arg) > 16:
                        # Verificar por padrões de tokens
                        for pattern in TOKEN_PATTERNS:
                            if re.match(pattern, arg):
                                arg = mask_partially(arg)
                                break
                        
                        # Verificar por palavras-chave sensíveis
                        if any(keyword in str(arg).lower() for keyword in SENSITIVE_KEYWORDS):
                            arg = mask_partially(arg)
                
                # Tentar mascarar objetos complexos
                elif isinstance(arg, (dict, list)):
                    arg = mask_sensitive_data(arg)
                
                safe_args.append(arg)
            
            # Mascaramento mais agressivo para kwargs
            safe_kwargs = {}
            for k, v in kwargs.items():
                # Se a chave contiver palavras sensíveis, mascarar o valor
                if any(keyword in k.lower() for keyword in SENSITIVE_KEYWORDS):
                    safe_kwargs[k] = '***'
                # Para outros valores, tentar mascarar se for string ou complexo
                elif isinstance(v, str):
                    if len(v) > 16 and (
                        any(keyword in v.lower() for keyword in SENSITIVE_KEYWORDS) or
                        any(re.search(pattern, v) for pattern in TOKEN_PATTERNS)
                    ):
                        safe_kwargs[k] = mask_partially(v)
                    else:
                        safe_kwargs[k] = v
                elif isinstance(v, (dict, list)):
                    safe_kwargs[k] = mask_sensitive_data(v)
                else:
                    safe_kwargs[k] = v
            
            func_name = func.__qualname__
            logger.log(level, f"Iniciando {func_name} - Args: {safe_args}, Kwargs: {safe_kwargs}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.log(level, f"Concluído {func_name} em {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                error_msg = str(e)
                # Mascarar dados sensíveis na mensagem de erro
                masked_error = mask_sensitive_data(error_msg)
                logger.error(f"Erro em {func_name} após {elapsed:.3f}s: {masked_error}", 
                             exc_info=True)
                raise
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)

# Configuração inicial do logger raiz
root_logger = setup_logging()
root_logger.debug(f"Sistema de logging inicializado - Nível: {LOG_LEVEL}")
