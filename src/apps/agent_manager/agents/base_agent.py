"""
Classe base para todos os agentes do sistema.
"""
import os
import time
import logging
from typing import Optional, Dict, Any
from agent_platform.core.logger import get_logger
from agent_platform.core.utils import TokenValidator

class BaseAgent:
    """
    Classe base para todos os agentes do sistema.
    Fornece funcionalidades comuns como logging, validação de tokens e gestão de contexto.
    """
    
    def __init__(self, openai_token: Optional[str] = None, github_token: Optional[str] = None, name: Optional[str] = None):
        """
        Inicializa o agente base.
        
        Args:
            openai_token: Token da API OpenAI
            github_token: Token do GitHub
            name: Nome do agente, usado para logging
            
        Raises:
            ValueError: Se os tokens obrigatórios não forem fornecidos
        """
        # Nome do agente (para logging)
        self.name = name or self.__class__.__name__
        self.logger = get_logger(self.name)
        
        # Tokens de API 
        self.openai_token = openai_token or os.environ.get("OPENAI_API_KEY", "")
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN", "")
        
        # Validar tokens
        self.validate_required_tokens()
    
    def validate_required_tokens(self):
        """
        Valida se os tokens obrigatórios estão presentes.
        Deve ser sobrescrito pelos agentes filhos se precisarem de validações específicas.
        
        Raises:
            ValueError: Se os tokens obrigatórios estiverem ausentes ou inválidos
        """
        # Validar tokens por padrão
        TokenValidator.validate_openai_token(self.openai_token, required=True)
        
        # O GitHub pode não ser necessário para todos os agentes
        # Subclasses específicas podem exigir ambos
    
    def log_memory_usage(self, label: str, start_time: Optional[float] = None):
        """
        Registra uso de memória e tempo (opcional) para fins de diagnóstico
        
        Args:
            label: Identificador do ponto de medição
            start_time: Tempo de início para cálculo de duração (opcional)
        """
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            log_msg = f"{label} | Memória: {memory_mb:.2f} MB"
            if start_time:
                duration = time.time() - start_time
                log_msg += f" | Tempo: {duration:.2f}s"
                
            self.logger.debug(log_msg)
            
        except ImportError:
            self.logger.debug(f"{label} | psutil não disponível para medição de memória")
        except Exception as e:
            self.logger.warning(f"Erro ao medir memória: {str(e)}") 