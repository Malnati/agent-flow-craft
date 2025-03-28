"""
Utilitários para manipulação segura de dados e informações sensíveis.
"""
import re
import os
from typing import Any, Dict, List, Union

# Lista de palavras-chave para identificar dados sensíveis
SENSITIVE_KEYWORDS = [
    'pass', 'senha', 'password', 
    'token', 'access_token', 'refresh_token', 'jwt', 
    'secret', 'api_key', 'apikey', 'key', 
    'auth', 'credential', 'oauth', 
    'private', 'signature'
]

def mask_sensitive_data(data: Any, mask_str: str = '***') -> Any:
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
        # Mascara padrões em strings (ex: chaves de API, tokens)
        patterns = [
            # Tokens e chaves de API comuns (OpenAI, GitHub)
            r'(sk-[a-zA-Z0-9]{20,})',
            r'(github_pat_[a-zA-Z0-9]{20,})',
            r'(ghp_[a-zA-Z0-9]{20,})',
            # JWT e tokens similares
            r'(eyJ[a-zA-Z0-9_-]{5,}\.eyJ[a-zA-Z0-9_-]{5,})',
            # Chaves de API e tokens genéricos
            r'([a-zA-Z0-9_-]{20,})'  # Identificar sequências longas que podem ser tokens
        ]
        
        masked_data = data
        for pattern in patterns:
            # Só aplicar regex em strings com comprimento suficiente (evita operações caras)
            if len(masked_data) > 20 and re.search(pattern, masked_data):
                # Use grupos de captura para substituir apenas os padrões
                masked_data = re.sub(pattern, mask_str, masked_data)
        
        return masked_data
    else:
        # Retorna o valor original para outros tipos
        return data

def get_env_status(var_name: str) -> str:
    """
    Retorna o status de uma variável de ambiente sem expor seu valor.
    
    Args:
        var_name: Nome da variável de ambiente
        
    Returns:
        String indicando o status da variável
    """
    value = os.environ.get(var_name)
    if not value:
        return "não definido"
    elif any(keyword in var_name.lower() for keyword in SENSITIVE_KEYWORDS):
        return "configurado"
    else:
        # Para variáveis não sensíveis, podemos retornar o valor
        # Mas aplicamos mascaramento para garantir segurança
        return mask_sensitive_data(value)

def log_env_status(logger, env_vars: List[str]) -> None:
    """
    Registra o status de múltiplas variáveis de ambiente de forma segura.
    
    Args:
        logger: Logger para registrar as informações
        env_vars: Lista de nomes de variáveis de ambiente
    """
    for var in env_vars:
        status = get_env_status(var)
        logger.info(f"Estado da variável {var}: {status}") 