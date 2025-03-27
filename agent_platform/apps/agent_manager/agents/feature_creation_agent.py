from autogen import AssistantAgent
from autogen.tools import tool
import subprocess
import json
import os
import logging
from slugify import slugify
import re
from django.conf import settings

# ... restante do código do agente, adaptando os caminhos ...

def _read_project_file_internal(file_path, max_lines=100):
    # Adaptar para usar caminhos relativos às configurações Django
    lines = []
    with open(file_path, 'r') as file:
        for idx, line in enumerate(file):
            if idx >= max_lines:
                break
            lines.append(line)
    return ''.join(lines)

class FeatureCreationAgent(AssistantAgent):
    def __init__(self, github_token, repo_owner, repo_name):
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.logger = logging.getLogger("apps.agent_manager.agents.feature_agent")
        self.check_github_auth()

    # ... restante do código do agente ...

    def create_pr_plan_file(self, issue_number, prompt_text, execution_plan, branch_name, suggestion=None):
        self.logger.info(f"Criando arquivo de plano para PR da issue #{issue_number}")
        
        # Uso do settings para determinar caminhos
        file_name = os.path.join(settings.MEDIA_ROOT, 'pr_plans', f'{issue_number}_feature_plan.md')
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        
        # ... restante do método ... 