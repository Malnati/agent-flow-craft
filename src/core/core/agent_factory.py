# Fábrica para criar diferentes tipos de agentes
import os
import sys
from pathlib import Path
from core.core.logger import get_logger, log_execution

# Tente importar funções de mascaramento de dados sensíveis
try:
    from core.core.utils import mask_sensitive_data, get_env_status
    has_utils = True
except ImportError:
    has_utils = False
    # Função básica de fallback para mascaramento
    def mask_sensitive_data(data, mask_str='***'):
        if isinstance(data, str) and any(s in data.lower() for s in ['token', 'key', 'secret', 'password']):
            # Mostrar parte do início e fim para debugging
            if len(data) > 10:
                return f"{data[:4]}{'*' * 12}{data[-4:] if len(data) > 8 else ''}"
            return mask_str
        return data

# Adicionar o diretório base ao path para permitir importações
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Logger específico para a fábrica de agentes
logger = get_logger(__name__)

try:
    # Importar os novos agentes do padrão de design separado
    from apps.agent_manager.agents.feature_coordinator_agent import FeatureCoordinatorAgent
    from apps.agent_manager.agents.concept_generation_agent import ConceptGenerationAgent
    from apps.agent_manager.agents.github_integration_agent import GitHubIntegrationAgent
    from apps.agent_manager.agents.plan_validator import PlanValidator
    from apps.agent_manager.agents.context_manager import ContextManager
    
    # Para compatibilidade com código existente, manter o agente legado
    from apps.agent_manager.agents.feature_creation_agent import FeatureCreationAgent
except ImportError as e:
    error_msg = mask_sensitive_data(str(e))
    logger.critical(f"FALHA - Importação de agentes | Erro: {error_msg}", exc_info=True)
    sys.exit(1)

class AgentFactory:
    """Fábrica para criar diferentes tipos de agentes"""
    
    @classmethod
    @log_execution
    def create_feature_agent(cls, github_token=None, repo_owner=None, repo_name=None, openai_token=None, target_dir=None):
        """
        Cria um agente de criação de features.
        NOTA: Esta função agora retorna o novo FeatureCoordinatorAgent,
        que coordena múltiplos agentes especializados.
        
        Para compatibilidade com código existente, também é mantido o método
        create_legacy_feature_agent() que retorna o agente original.
        """
        logger.info(f"INÍCIO - create_feature_agent | Parâmetros: owner={repo_owner}, repo={repo_name}")
        
        try:
            # Usar variáveis de ambiente se os parâmetros não forem fornecidos
            github_token = github_token or os.environ.get('GITHUB_TOKEN', '')
            repo_owner = repo_owner or os.environ.get('GITHUB_OWNER', '')
            repo_name = repo_name or os.environ.get('GITHUB_REPO', '')
            openai_token = openai_token or os.environ.get('OPENAI_API_KEY', '')
            
            # Log seguro do status do token
            if has_utils:
                github_status = get_env_status('GITHUB_TOKEN')
                openai_status = get_env_status('OPENAI_API_KEY')
                logger.debug(f"Status do token GitHub: {github_status}")
                logger.debug(f"Status do token OpenAI: {openai_status}")
            else:
                github_available = "disponível" if github_token else "ausente"
                openai_available = "disponível" if openai_token else "ausente"
                logger.debug(f"Status do token GitHub: {github_available}")
                logger.debug(f"Status do token OpenAI: {openai_available}")
            
            if not github_token:
                logger.warning("ALERTA - Token GitHub ausente | Funcionalidades GitHub serão limitadas")
                
            if not openai_token:
                logger.warning("ALERTA - Token OpenAI ausente | Funcionalidades de IA serão limitadas")
            
            # Criar o novo agente coordenador
            agent = FeatureCoordinatorAgent(
                github_token=github_token,
                openai_token=openai_token,
                repo_owner=repo_owner,
                repo_name=repo_name,
                target_dir=target_dir
            )
            logger.info(f"SUCESSO - Agente coordenador criado | owner={repo_owner}, repo={repo_name}")
            return agent
            
        except Exception as e:
            # Mascarar possíveis tokens na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"FALHA - create_feature_agent | Erro: {error_msg}", exc_info=True)
            raise
    
    @classmethod
    @log_execution
    def create_legacy_feature_agent(cls, github_token=None, repo_owner=None, repo_name=None):
        """
        Cria um agente de criação de features usando a classe original.
        DEPRECIADO: Use create_feature_agent() para obter o novo agente coordenador.
        """
        logger.warning("DEPRECIADO - create_legacy_feature_agent | Use create_feature_agent para o novo agente")
        logger.info(f"INÍCIO - create_legacy_feature_agent | Parâmetros: owner={repo_owner}, repo={repo_name}")
        
        try:
            # Usar variáveis de ambiente se os parâmetros não forem fornecidos
            github_token = github_token or os.environ.get('GITHUB_TOKEN', '')
            repo_owner = repo_owner or os.environ.get('GITHUB_OWNER', '')
            repo_name = repo_name or os.environ.get('GITHUB_REPO', '')
            
            # Log seguro do status do token
            if has_utils:
                token_status = get_env_status('GITHUB_TOKEN')
                logger.debug(f"Status do token GitHub: {token_status}")
            else:
                token_available = "disponível" if github_token else "ausente"
                logger.debug(f"Status do token GitHub: {token_available}")
            
            if not github_token:
                logger.warning("ALERTA - Token GitHub ausente | Funcionalidades GitHub serão limitadas")
            
            agent = FeatureCreationAgent(github_token, repo_owner, repo_name)
            logger.info(f"SUCESSO - Agente legado criado | owner={repo_owner}, repo={repo_name}")
            return agent
            
        except Exception as e:
            # Mascarar possíveis tokens na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"FALHA - create_legacy_feature_agent | Erro: {error_msg}", exc_info=True)
            raise
    
    @classmethod
    @log_execution
    def create_plan_validator(cls):
        """Cria um validador de planos"""
        logger.info("INÍCIO - create_plan_validator")
        
        try:
            validator_logger = get_logger("plan_validator")
            validator = PlanValidator(validator_logger)
            logger.info("SUCESSO - Validador de planos criado")
            return validator
            
        except Exception as e:
            # Mascarar possíveis tokens na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"FALHA - create_plan_validator | Erro: {error_msg}", exc_info=True)
            raise
    
    @classmethod
    @log_execution
    def create_concept_agent(cls, openai_token=None):
        """Cria um agente de geração de conceitos"""
        logger.info("INÍCIO - create_concept_agent")
        
        try:
            # Usar variável de ambiente se o parâmetro não for fornecido
            openai_token = openai_token or os.environ.get('OPENAI_API_KEY', '')
            
            # Log seguro do status do token
            if has_utils:
                token_status = get_env_status('OPENAI_API_KEY')
                logger.debug(f"Status do token OpenAI: {token_status}")
            else:
                token_available = "disponível" if openai_token else "ausente"
                logger.debug(f"Status do token OpenAI: {token_available}")
            
            if not openai_token:
                logger.warning("ALERTA - Token OpenAI ausente | Funcionalidades limitadas")
            
            agent = ConceptGenerationAgent(openai_token)
            logger.info("SUCESSO - Agente de conceito criado")
            return agent
            
        except Exception as e:
            # Mascarar possíveis tokens na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"FALHA - create_concept_agent | Erro: {error_msg}", exc_info=True)
            raise
    
    @classmethod
    @log_execution
    def create_github_agent(cls, github_token=None, repo_owner=None, repo_name=None, target_dir=None):
        """Cria um agente de integração com GitHub"""
        logger.info(f"INÍCIO - create_github_agent | Parâmetros: owner={repo_owner}, repo={repo_name}, target_dir={target_dir}")
        
        try:
            # Usar variáveis de ambiente se os parâmetros não forem fornecidos
            github_token = github_token or os.environ.get('GITHUB_TOKEN', '')
            repo_owner = repo_owner or os.environ.get('GITHUB_OWNER', '')
            repo_name = repo_name or os.environ.get('GITHUB_REPO', '')
            
            # Log seguro do status do token
            if has_utils:
                token_status = get_env_status('GITHUB_TOKEN')
                logger.debug(f"Status do token GitHub: {token_status}")
            else:
                token_available = "disponível" if github_token else "ausente"
                logger.debug(f"Status do token GitHub: {token_available}")
            
            if not github_token:
                logger.warning("ALERTA - Token GitHub ausente | Funcionalidades GitHub serão limitadas")
            
            agent = GitHubIntegrationAgent(github_token, repo_owner, repo_name, target_dir)
            logger.info(f"SUCESSO - Agente GitHub criado | owner={repo_owner}, repo={repo_name}")
            return agent
            
        except Exception as e:
            # Mascarar possíveis tokens na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"FALHA - create_github_agent | Erro: {error_msg}", exc_info=True)
            raise
    
    @classmethod
    @log_execution
    def create_context_manager(cls, base_dir='agent_context'):
        """Cria um gerenciador de contexto para transferência entre agentes"""
        logger.info(f"INÍCIO - create_context_manager | Base dir: {base_dir}")
        
        try:
            manager = ContextManager(base_dir)
            logger.info("SUCESSO - Gerenciador de contexto criado")
            return manager
            
        except Exception as e:
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"FALHA - create_context_manager | Erro: {error_msg}", exc_info=True)
            raise
