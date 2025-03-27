from django.conf import settings
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
import os
from ..agents.feature_creation_agent import FeatureCreationAgent

class AgentFactory:
    """Fábrica para criar diferentes tipos de agentes"""
    
    @classmethod
    def create_feature_agent(cls, github_token=None, repo_owner=None, repo_name=None):
        """Cria um agente de criação de features"""
        github_token = github_token or settings.GITHUB_TOKEN
        repo_owner = repo_owner or settings.GITHUB_OWNER
        repo_name = repo_name or settings.GITHUB_REPO
        
        return FeatureCreationAgent(github_token, repo_owner, repo_name)
    
    @classmethod
    def create_autogen_assistant(cls, name="Assistant", system_message=None):
        """Cria um agente assistente AutoGen"""
        return AssistantAgent(
            name=name,
            system_message=system_message or "Você é um assistente útil.",
            llm_config=settings.AUTOGEN_CONFIG
        )
    
    @classmethod
    def create_autogen_user_proxy(cls, name="UserProxy"):
        """Cria um agente proxy de usuário AutoGen"""
        return UserProxyAgent(
            name=name,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={"work_dir": "coding"}
        ) 