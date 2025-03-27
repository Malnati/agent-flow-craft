
# Configurações específicas para agentes
import os
from pathlib import Path

# Constrói caminhos dentro do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Configurações do OpenAI
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Configurações do GitHub
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITHUB_OWNER = os.environ.get('GITHUB_OWNER', '')
GITHUB_REPO = os.environ.get('GITHUB_REPO', '')

# Configurações de caminhos para agentes
AGENT_SESSION_BASE_PATH = os.path.join(BASE_DIR, 'run', 'agents', 'sessions')
AGENT_CONFIG_PATH = os.path.join(BASE_DIR, 'configs', 'agents')

# Exemplo de configuração do AutoGen
AUTOGEN_CONFIG = {
    "default_llm_config": {
        "config_list": [
            {
                "model": "gpt-4",
                "api_key": OPENAI_API_KEY
            }
        ]
    }
}