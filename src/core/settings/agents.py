# Configurações específicas para agentes
import os
from pathlib import Path
from core.core.logger import get_logger, log_execution

logger = get_logger(__name__)

@log_execution
def load_agent_settings():
    """Carrega e valida as configurações dos agentes"""
    logger.info("INÍCIO - load_agent_settings | Carregando configurações")
    
    try:
        # Constrói caminhos dentro do projeto
        base_dir = Path(__file__).resolve().parent.parent.parent
        logger.debug(f"Diretório base: {base_dir}")

        # Configurações do OpenAI
        openai_api_key = os.environ.get('OPENAI_API_KEY', '')
        if not openai_api_key:
            logger.warning("ALERTA - OPENAI_API_KEY não definida")

        # Configurações do GitHub
        github_token = os.environ.get('GITHUB_TOKEN', '')
        github_owner = os.environ.get('GITHUB_OWNER', '')
        github_repo = os.environ.get('GITHUB_REPO', '')

        if not all([github_token, github_owner, github_repo]):
            logger.warning("ALERTA - Configurações GitHub incompletas")

        # Configurações de caminhos para agentes
        agent_session_path = os.path.join(base_dir, 'run', 'agents', 'sessions')
        agent_config_path = os.path.join(base_dir, 'configs', 'agents')

        # Criar diretórios se não existirem
        os.makedirs(agent_session_path, exist_ok=True)
        os.makedirs(agent_config_path, exist_ok=True)

        # Configuração do AutoGen
        autogen_config = {
            "default_llm_config": {
                "config_list": [
                    {
                        "model": "gpt-4",
                        "api_key": openai_api_key
                    }
                ]
            }
        }

        logger.info("SUCESSO - Configurações carregadas")
        return {
            'OPENAI_API_KEY': openai_api_key,
            'GITHUB_TOKEN': github_token,
            'GITHUB_OWNER': github_owner,
            'GITHUB_REPO': github_repo,
            'AGENT_SESSION_BASE_PATH': agent_session_path,
            'AGENT_CONFIG_PATH': agent_config_path,
            'AUTOGEN_CONFIG': autogen_config
        }
        
    except Exception as e:
        logger.error(f"FALHA - load_agent_settings | Erro: {str(e)}", exc_info=True)
        raise

# Carrega as configurações
agent_settings = load_agent_settings()
globals().update(agent_settings)