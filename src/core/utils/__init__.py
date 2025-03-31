"""
Utilitários para manipulação segura de dados e informações sensíveis.
Fornece ferramentas para validação de tokens, mascaramento de dados sensíveis
e gerenciamento de variáveis de ambiente.
"""

from core.core.utils import TokenValidator

# Definir funções de utilidade
def mask_sensitive_data(data, mask_str='***'):
    """
    Mascara dados sensíveis em strings e dicionários.
    
    Args:
        data: Dados a serem mascarados (string, dict ou outro tipo)
        mask_str: String de substituição para dados sensíveis
        
    Returns:
        Dados com informações sensíveis mascaradas
    """
    from core.core.logger import mask_sensitive_data as logger_mask_sensitive_data
    return logger_mask_sensitive_data(data, mask_str)

def get_env_status(var_name):
    """
    Retorna o status de uma variável de ambiente sem expor seu valor.
    
    Args:
        var_name: Nome da variável de ambiente
        
    Returns:
        String indicando o status da variável
    """
    import os
    from core.core.logger import mask_sensitive_data
    
    # Lista de palavras-chave para identificar dados sensíveis
    SENSITIVE_KEYWORDS = [
        'pass', 'senha', 'password', 
        'token', 'access_token', 'refresh_token', 'jwt', 
        'secret', 'api_key', 'apikey', 'key', 
        'auth', 'credential', 'oauth', 
        'private', 'signature'
    ]
    
    value = os.environ.get(var_name)
    if not value:
        return "não definido"
    elif any(keyword in var_name.lower() for keyword in SENSITIVE_KEYWORDS):
        return "configurado"
    else:
        # Para variáveis não sensíveis, podemos retornar o valor
        # Mas aplicamos mascaramento para garantir segurança
        return mask_sensitive_data(value)

__all__ = ['mask_sensitive_data', 'get_env_status', 'TokenValidator']
