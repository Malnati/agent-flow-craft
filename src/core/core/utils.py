"""
Utilitários para manipulação segura de dados e informações sensíveis.
"""
import os
import re
from typing import Any, Dict, List, Union, Optional

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
        logger.info(f"Variável de ambiente {var}: {status}")

class TokenValidator:
    """
    Validador de tokens de API e chaves de ambiente.
    Garante que os tokens necessários estejam presentes e válidos.
    """
    
    @staticmethod
    def validate_token(token: Optional[str], token_name: str, required: bool = True) -> bool:
        """
        Valida se um token está presente e tem uma estrutura mínima válida.
        
        Args:
            token: O token a ser validado
            token_name: Nome do token para mensagens de erro
            required: Se o token é obrigatório
            
        Returns:
            bool: True se o token for válido, False caso contrário
            
        Raises:
            ValueError: Se o token for obrigatório e estiver ausente ou inválido
        """
        if not token or token.strip() == "":
            if required:
                raise ValueError(f"Token {token_name} é obrigatório mas não foi encontrado nas variáveis de ambiente")
            return False
            
        # Verificação básica de estrutura mínima (pelo menos 10 caracteres, sem espaços)
        if len(token) < 10 or " " in token:
            if required:
                raise ValueError(f"Token {token_name} parece inválido (formato incorreto)")
            return False
            
        return True
    
    @staticmethod
    def validate_openai_token(token: Optional[str] = None, required: bool = True) -> bool:
        """
        Valida token da OpenAI, com verificações específicas para o formato do token.
        
        Args:
            token: Token da OpenAI. Se None, será buscado na variável de ambiente
            required: Se o token é obrigatório
            
        Returns:
            bool: True se o token for válido, False caso contrário
            
        Raises:
            ValueError: Se o token for obrigatório e estiver ausente ou inválido
        """
        # Se não fornecido, tenta buscar da variável de ambiente
        if token is None:
            token = os.environ.get("OPENAI_API_KEY", "")
            
        # Verificação específica para tokens da OpenAI (geralmente começam com "sk-")
        if token and not token.startswith("sk-"):
            if required:
                raise ValueError("Token da OpenAI inválido (deve começar com 'sk-')")
            return False
            
        return TokenValidator.validate_token(token, "OpenAI", required)
        
    @staticmethod
    def validate_github_token(token: Optional[str] = None, required: bool = True) -> bool:
        """
        Valida token do GitHub, com verificações específicas para o formato do token.
        
        Args:
            token: Token do GitHub. Se None, será buscado na variável de ambiente
            required: Se o token é obrigatório
            
        Returns:
            bool: True se o token for válido, False caso contrário
            
        Raises:
            ValueError: Se o token for obrigatório e estiver ausente ou inválido
        """
        # Se não fornecido, tenta buscar da variável de ambiente
        if token is None:
            token = os.environ.get("GITHUB_TOKEN", "")
            
        # GitHub tokens geralmente têm um formato específico, como começar com "ghp_"
        # Mas isso pode variar, então faremos uma verificação básica
        
        return TokenValidator.validate_token(token, "GitHub", required)
    
    @staticmethod
    def validate_all_required_tokens() -> bool:
        """
        Valida todos os tokens obrigatórios para o sistema.
        
        Returns:
            bool: True se todos os tokens obrigatórios estiverem válidos
            
        Raises:
            ValueError: Detalhando quais tokens estão faltando ou são inválidos
        """
        missing_tokens = []
        
        try:
            TokenValidator.validate_openai_token(required=True)
        except ValueError as e:
            missing_tokens.append(str(e))
            
        try:
            TokenValidator.validate_github_token(required=True)
        except ValueError as e:
            missing_tokens.append(str(e))
            
        if missing_tokens:
            raise ValueError(f"Tokens obrigatórios faltando ou inválidos: {', '.join(missing_tokens)}")
            
        return True 