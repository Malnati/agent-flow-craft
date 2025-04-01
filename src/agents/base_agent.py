"""
Classe base para todos os agentes do sistema.
"""
import os
import time
from typing import Optional
from src.core.logger import get_logger
from src.core.utils import TokenValidator

class BaseAgent:
    """
    Classe base para todos os agentes do sistema.
    Fornece funcionalidades comuns como logging, validação de tokens e gestão de contexto.
    """
    
    def __init__(self, openai_token: Optional[str] = None, github_token: Optional[str] = None, 
                 name: Optional[str] = None, model: Optional[str] = None, 
                 elevation_model: Optional[str] = None, force: bool = False):
        """
        Inicializa o agente base.
        
        Args:
            openai_token: Token da API OpenAI
            github_token: Token do GitHub
            name: Nome do agente, usado para logging
            model: Modelo principal a ser utilizado
            elevation_model: Modelo de elevação a ser usado em caso de falha
            force: Se True, usa diretamente o modelo de elevação
            
        Raises:
            ValueError: Se os tokens obrigatórios não forem fornecidos
        """
        # Nome do agente (para logging)
        self.name = name or self.__class__.__name__
        self.logger = get_logger(self.name)
        
        # Tokens de API 
        self.openai_token = openai_token or os.environ.get("OPENAI_API_KEY", "")
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN", "")
        
        # Configurações de modelo e elevação
        self.model = model
        self.elevation_model = elevation_model
        self.force = force
        
        # Se force=True, já começa com o modelo de elevação como modelo ativo
        if self.force and self.elevation_model:
            self.logger.info(f"Modo force ativado, usando diretamente o modelo de elevação: {self.elevation_model}")
            self.model = self.elevation_model
        
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
    
    def set_model(self, model):
        """
        Define o modelo a ser utilizado.
        
        Args:
            model (str): Nome do modelo
        """
        self.logger.info(f"INÍCIO - set_model | Modelo anterior: {self.model} | Novo modelo: {model}")
        self.model = model
        self.logger.info(f"SUCESSO - Modelo alterado para: {self.model}")
        return self.model
    
    def set_elevation_model(self, elevation_model):
        """
        Define o modelo de elevação a ser utilizado.
        
        Args:
            elevation_model (str): Nome do modelo de elevação
        """
        self.logger.info(f"INÍCIO - set_elevation_model | Modelo anterior: {self.elevation_model} | Novo modelo: {elevation_model}")
        self.elevation_model = elevation_model
        self.logger.info(f"SUCESSO - Modelo de elevação alterado para: {self.elevation_model}")
        return self.elevation_model
    
    def use_elevation_model(self):
        """
        Troca para o modelo de elevação em caso de falha do modelo principal.
        
        Returns:
            bool: True se a elevação foi possível, False caso contrário
        """
        if not self.elevation_model:
            self.logger.warning("Modelo de elevação não configurado, não é possível elevar")
            return False
            
        self.logger.info(f"Elevando de {self.model} para {self.elevation_model}")
        self.model = self.elevation_model
        return True
    
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