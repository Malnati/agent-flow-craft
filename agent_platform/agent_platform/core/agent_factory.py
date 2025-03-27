# Fábrica para criar diferentes tipos de agentes
import os
import sys
from pathlib import Path
from agent_platform.core.logger import get_logger, log_execution

# Adicionar o diretório base ao path para permitir importações
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Logger específico para a fábrica de agentes
logger = get_logger(__name__)

try:
    from apps.agent_manager.agents.feature_creation_agent import FeatureCreationAgent
    from apps.agent_manager.agents.plan_validator import PlanValidator
except ImportError as e:
    logger.critical(f"FALHA - Importação de agentes | Erro: {str(e)}", exc_info=True)
    sys.exit(1)

class AgentFactory:
    """Fábrica para criar diferentes tipos de agentes"""
    
    @classmethod
    @log_execution
    def create_feature_agent(cls, github_token=None, repo_owner=None, repo_name=None):
        """Cria um agente de criação de features"""
        logger.info(f"INÍCIO - create_feature_agent | Parâmetros: owner={repo_owner}, repo={repo_name}")
        
        try:
            # Usar variáveis de ambiente se os parâmetros não forem fornecidos
            github_token = github_token or os.environ.get('GITHUB_TOKEN', '')
            repo_owner = repo_owner or os.environ.get('GITHUB_OWNER', '')
            repo_name = repo_name or os.environ.get('GITHUB_REPO', '')
            
            if not github_token:
                logger.warning("ALERTA - Token GitHub ausente | Funcionalidades GitHub serão limitadas")
            
            agent = FeatureCreationAgent(github_token, repo_owner, repo_name)
            logger.info(f"SUCESSO - Agente criado | owner={repo_owner}, repo={repo_name}")
            return agent
            
        except Exception as e:
            logger.error(f"FALHA - create_feature_agent | Erro: {str(e)}", exc_info=True)
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
            logger.error(f"FALHA - create_plan_validator | Erro: {str(e)}", exc_info=True)
            raise
