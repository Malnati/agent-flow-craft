# Fábrica para criar diferentes tipos de agentes
import os
import sys
from pathlib import Path

# Adicionar o diretório base ao path para permitir importações
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    from apps.agent_manager.agents.feature_creation_agent import FeatureCreationAgent
    from apps.agent_manager.agents.plan_validator import PlanValidator
except ImportError as e:
    print(f"Erro ao importar agentes: {e}")
    sys.exit(1)

class AgentFactory:
    """Fábrica para criar diferentes tipos de agentes"""
    
    @classmethod
    def create_feature_agent(cls, github_token=None, repo_owner=None, repo_name=None):
        """Cria um agente de criação de features"""
        # Usar variáveis de ambiente se os parâmetros não forem fornecidos
        github_token = github_token or os.environ.get('GITHUB_TOKEN', '')
        repo_owner = repo_owner or os.environ.get('GITHUB_OWNER', '')
        repo_name = repo_name or os.environ.get('GITHUB_REPO', '')
        
        return FeatureCreationAgent(github_token, repo_owner, repo_name)
    
    @classmethod
    def create_plan_validator(cls):
        """Cria um validador de planos"""
        import logging
        logger = logging.getLogger("plan_validator")
        
        return PlanValidator(logger)
