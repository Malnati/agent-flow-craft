"""
Classe base para todos os agentes do sistema.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import os

from src.core.utils.env import validate_env
from src.core.utils.model_manager import ModelManager


class BaseAgent(ABC):
    """Classe base para todos os agentes do sistema."""

    def __init__(
        self,
        model_name: str = "gpt-4-turbo",
        elevation_model: Optional[str] = None,
        force_model: bool = False,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> None:
        """
        Inicializa o agente.

        Args:
            model_name: Nome do modelo a ser usado.
            elevation_model: Modelo alternativo para fallback.
            force_model: Se True, força o uso do modelo especificado sem fallback.
            api_key: Chave da API para o modelo.
            timeout: Tempo limite para requisições ao modelo.
            max_retries: Número máximo de tentativas em caso de falha.
            temperature: Temperatura para geração de texto pelo modelo.
            max_tokens: Número máximo de tokens para geração de texto.
        """
        # Valida variáveis de ambiente
        validate_env()

        # Recupera chave da API de args ou variáveis de ambiente
        self.api_key = api_key or os.environ.get("API_KEY")
        if not self.api_key:
            raise ValueError("Chave da API não fornecida e não encontrada nas variáveis de ambiente")

        # Inicializa gerenciador de modelos
        self.model_manager = ModelManager()
        self.model_name = model_name
        self.elevation_model = elevation_model
        self.force_model = force_model
        self.timeout = timeout
        self.max_retries = max_retries
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Verifica se o modelo está disponível
        if not self.model_manager.get_model_config(model_name):
            raise ValueError(f"Modelo {model_name} não disponível")

        # Se tiver modelo de elevação, verifica se está disponível
        if elevation_model and not self.model_manager.get_model_config(elevation_model):
            raise ValueError(f"Modelo de elevação {elevation_model} não disponível")

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        Gera uma resposta usando o modelo configurado.

        Args:
            prompt: O prompt para gerar a resposta.
            **kwargs: Argumentos adicionais para a API do modelo.

        Returns:
            A resposta gerada pelo modelo.

        Raises:
            Exception: Se ocorrer um erro na geração.
        """
        try:
            response = await self.model_manager.generate(
                prompt=prompt,
                model_name=self.model_name,
                elevation_model=self.elevation_model,
                force=self.force_model,
                api_key=self.api_key,
                timeout=self.timeout,
                max_retries=self.max_retries,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs,
            )
            return str(response)
        except Exception as e:
            # Se não tiver modelo de elevação ou estiver forçando o modelo, propaga o erro
            if not self.elevation_model or self.force_model:
                raise e

            # Tenta usar o modelo de elevação
            return await self.model_manager.generate(
                prompt=prompt,
                model_name=self.elevation_model,
                force=True,
                api_key=self.api_key,
                timeout=self.timeout,
                max_retries=self.max_retries,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs,
            )

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Executa a tarefa principal do agente.

        Args:
            **kwargs: Argumentos específicos do agente.

        Returns:
            Resultado da execução.
        """

    def set_model(self, model):
        """
        Define o modelo a ser utilizado.
        
        Args:
            model (str): Nome do modelo
        """
        self.model_name = model
        return self.model_name
    
    def set_elevation_model(self, elevation_model):
        """
        Define o modelo de elevação a ser utilizado.
        
        Args:
            elevation_model (str): Nome do modelo de elevação
        """
        self.elevation_model = elevation_model
        return self.elevation_model
    
    def handle_model_error(self, error: Dict[str, Any]) -> Optional[str]:
        """
        Trata erros de modelo e tenta fazer fallback quando possível.
        
        Args:
            error: Detalhes do erro retornado pela API
            
        Returns:
            str: Próximo modelo a tentar, ou None se não houver opção
            
        Raises:
            RuntimeError: Se não houver mais modelos disponíveis
        """
        # Marca modelo atual como indisponível
        self.model_manager.mark_model_unavailable(self.model, error)
        
        # Se temos modelo de elevação e ainda não tentamos
        if self.elevation_model and self.model != self.elevation_model:
            if self.model_manager.is_model_available(self.elevation_model):
                self.logger.info(f"Tentando modelo de elevação: {self.elevation_model}")
                return self.elevation_model
        
        # Procura próximo modelo disponível
        next_model = self.model_manager.get_next_available_model(self.model)
        if next_model:
            self.logger.info(f"Tentando próximo modelo disponível: {next_model}")
            return next_model
            
        # Se chegamos aqui, não há mais opções
        error_msg = self.model_manager.get_error_message(self.model, error)
        self.logger.error(f"Sem modelos disponíveis. Último erro: {error_msg}")
        raise RuntimeError(error_msg)
    
    def execute_with_fallback(self, func, *args, **kwargs):
        """
        Executa uma função com suporte a fallback de modelos.
        
        Args:
            func: Função a ser executada
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Any: Resultado da função
            
        Raises:
            RuntimeError: Se não for possível executar com nenhum modelo
        """
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Tenta extrair detalhes do erro
                error_dict = {}
                if hasattr(e, 'response'):
                    error_dict = e.response.json().get('error', {})
                elif hasattr(e, '__dict__'):
                    error_dict = e.__dict__
                
                # Se não é erro de quota ou modelo, propaga
                if not error_dict.get('code') in ['insufficient_quota', 'model_not_available']:
                    raise
                
                # Tenta próximo modelo
                next_model = self.handle_model_error(error_dict)
                if not next_model:
                    raise RuntimeError("Sem modelos disponíveis para continuar a execução")
    
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