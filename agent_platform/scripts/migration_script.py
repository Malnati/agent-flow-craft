import os
import shutil
import re

# Diretórios base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR = os.path.join(BASE_DIR, 'agent_platform')

# 1. Migrar agentes
os.makedirs(os.path.join(TARGET_DIR, 'apps/agent_manager/agents'), exist_ok=True)
shutil.copy(
    os.path.join(BASE_DIR, 'agents/feature_creation_agent.py'),
    os.path.join(TARGET_DIR, 'apps/agent_manager/agents/feature_creation_agent.py')
)
shutil.copy(
    os.path.join(BASE_DIR, 'agents/plan_validator.py'),
    os.path.join(TARGET_DIR, 'apps/agent_manager/agents/plan_validator.py')
)

# 2. Migrar configurações
os.makedirs(os.path.join(TARGET_DIR, 'configs/agents'), exist_ok=True)
shutil.copy(
    os.path.join(BASE_DIR, 'config/plan_requirements.yaml'),
    os.path.join(TARGET_DIR, 'configs/agents/plan_requirements.yaml')
)

# 3. Migrar scripts como management commands
os.makedirs(os.path.join(TARGET_DIR, 'apps/agent_manager/management/commands'), exist_ok=True)

# Adaptar script para comando Django
with open(os.path.join(BASE_DIR, 'scripts/start_feature_agent.py'), 'r') as f:
    content = f.read()

# Transformar em comando Django
command_content = """from django.core.management.base import BaseCommand
import os
import sys

class Command(BaseCommand):
    help = 'Inicia o agente de criação de features'

    def add_arguments(self, parser):
        parser.add_argument('prompt', type=str, help='Prompt para o agente')
        parser.add_argument('execution_plan', type=str, help='Plano de execução')
        parser.add_argument('--token', type=str, help='GitHub token')
        parser.add_argument('--owner', type=str, help='Repository owner')
        parser.add_argument('--repo', type=str, help='Repository name')
        parser.add_argument('--openai_token', type=str, help='Token da OpenAI')
        parser.add_argument('--max_attempts', type=int, help='Número máximo de tentativas', default=3)
        parser.add_argument('--config', type=str, help='Arquivo de configuração', 
                        default="config/plan_requirements.yaml")

    def handle(self, *args, **options):
        # Aqui vai o código do script original adaptado para Django
        self.stdout.write(self.style.SUCCESS('Agente iniciado com sucesso!'))
"""

with open(os.path.join(TARGET_DIR, 'apps/agent_manager/management/commands/start_feature_agent.py'), 'w') as f:
    f.write(command_content)

# 4. Migrar documentação
os.makedirs(os.path.join(TARGET_DIR, 'docs'), exist_ok=True)
if os.path.exists(os.path.join(BASE_DIR, 'docs')):
    for item in os.listdir(os.path.join(BASE_DIR, 'docs')):
        source = os.path.join(BASE_DIR, 'docs', item)
        target = os.path.join(TARGET_DIR, 'docs', item)
        if os.path.isdir(source):
            shutil.copytree(source, target)
        else:
            shutil.copy(source, target)

# 5. Migrar arquivos raiz importantes
root_files = ['pyproject.toml', 'README.md', 'CHANGELOG.md', 'LICENSE']
for file in root_files:
    if os.path.exists(os.path.join(BASE_DIR, file)):
        shutil.copy(
            os.path.join(BASE_DIR, file),
            os.path.join(TARGET_DIR, file)
        )

print("Migração básica concluída. Você agora precisa configurar as settings Django.") 