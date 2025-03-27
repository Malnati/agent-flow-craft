"""
Configurações específicas para agentes
"""
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Configurações do OpenAI
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')

# Configurações do GitHub
GITHUB_TOKEN = config('GITHUB_TOKEN', default='')
GITHUB_OWNER = config('GITHUB_OWNER', default='')
GITHUB_REPO = config('GITHUB_REPO', default='')

# Configurações de caminhos para agentes
AGENT_SESSION_BASE_PATH = os.path.join(BASE_DIR, 'run', 'agents', 'sessions')
AGENT_CONFIG_PATH = os.path.join(BASE_DIR, 'configs', 'agents')

# Configurações do AutoGen
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