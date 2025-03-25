from autogen import AssistantAgent
from autogen.tools import tool
import subprocess
import json
import os
import logging
from slugify import slugify
import re

@tool
def list_project_files(directory=".", max_depth=2):
    """
    Lista recursivamente arquivos em um diretório até um nível máximo de profundidade.
    """
    result = []
    for root, dirs, files in os.walk(directory):
        depth = root[len(directory):].count(os.sep)
        if depth < max_depth:
            for file in files:
                result.append(os.path.join(root, file))
        else:
            dirs.clear()
    return result

@tool
def read_project_file(file_path, max_lines=100):
    """
    Lê até max_lines de um arquivo de texto e retorna como string.
    """
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
        self.logger = logging.getLogger("feature_agent")
        self.check_github_auth()

    def check_github_auth(self):
        self.logger.info("Verificando autenticação do GitHub CLI...")
        try:
            subprocess.run(['gh', 'auth', 'status'], check=True, capture_output=True, timeout=15)
            self.logger.info("Autenticação do GitHub verificada com sucesso.")
        except subprocess.CalledProcessError:
            self.logger.error("Falha na autenticação do GitHub CLI. Execute 'gh auth login' para autenticar.")
            raise

    def create_github_issue(self, title, body):
        self.logger.info(f"Criando issue: {title}")

        result = subprocess.run(
            [
                'gh', 'issue', 'create',
                '--repo', f'{self.repo_owner}/{self.repo_name}',
                '--title', title,
                '--body', body
            ],
            capture_output=True, text=True, check=True, timeout=30
        )

        output = result.stdout.strip()
        self.logger.info(f"Saída da criação da issue: {output}")

        # Extrair o número da issue da URL retornada
        match = re.search(r'/issues/(\d+)', output)
        if match:
            issue_number = int(match.group(1))
            self.logger.info(f"Issue #{issue_number} criada e capturada com sucesso")
            return issue_number
        else:
            self.logger.error("Falha ao extrair número da issue a partir da saída.")
            raise Exception("Falha ao capturar número da issue.")

    def create_branch(self, branch_name):
        self.logger.info(f"Criando branch: {branch_name}")
        
        subprocess.run(['git', 'checkout', '-b', branch_name], check=True, timeout=30)
        subprocess.run(['git', 'push', '--set-upstream', 'origin', branch_name], check=True, timeout=30)
        self.logger.info(f"Branch {branch_name} criada e enviada para o repositório remoto")

    def create_pr_plan_file(self, issue_number, prompt_text, execution_plan, branch_name):
        self.logger.info(f"Criando arquivo de plano para PR da issue #{issue_number}")
        
        file_name = f'docs/pr/{issue_number}_feature_plan.md'
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        
        with open(file_name, 'w') as f:
            f.write(f'# Plano de execução para a issue #{issue_number}\n\n')
            f.write(f'**Prompt recebido:** {prompt_text}\n\n')
            f.write('**Plano de execução gerado automaticamente:**\n\n')
            f.write('## Entregáveis:\n\n')
            f.write('- **Entregável 1:** Descrição breve\n')
            f.write('  - **Dependências:**\n    - Dependência A\n    - Dependência B\n')
            f.write('  - **Exemplo:**\n    - Exemplo concreto de uso\n')
            f.write('  - **Critérios de aceite:**\n    - Critério 1\n    - Critério 2\n')
            f.write('  - **Troubleshooting:**\n    - Possível falha e como corrigir\n')
            f.write('  - **Passo-a-passo:**\n    1. Passo inicial\n    2. Passo seguinte\n\n')
            f.write('- **Entregável 2:** Descrição breve\n')
            f.write('  - **Dependências:**\n    - Dependência X\n')
            f.write('  - **Exemplo:**\n    - Exemplo de saída esperada\n')
            f.write('  - **Critérios de aceite:**\n    - Checklist de validação\n')
            f.write('  - **Troubleshooting:**\n    - Erros comuns e resolução\n')
            f.write('  - **Passo-a-passo:**\n    1. Passo inicial\n    2. Passo seguinte\n\n')
            f.write('## Observações Finais:\n')
            f.write('- O agente deve consultar o histórico de commits e arquivos do projeto para enriquecer o plano.\n')
            f.write('- Todos os exemplos devem estar alinhados ao codebase atual.\n')
        
        subprocess.run(['git', 'add', file_name], check=True, timeout=30)
        subprocess.run(['git', 'commit', '-m', f'Add PR plan file for issue #{issue_number}'], check=True, timeout=30)
        subprocess.run(['git', 'push'], check=True, timeout=30)
        self.logger.info(f"Arquivo de plano de PR criado e enviado para o repositório remoto")

    def create_pull_request(self, branch_name, issue_number):
        self.logger.info(f"Criando pull request para a issue #{issue_number} da branch {branch_name}")
        
        subprocess.run([
            'gh', 'pr', 'create',
            '--base', 'main',
            '--head', branch_name,
            '--title', f'Automated PR for issue #{issue_number}',
            '--body', f'Closes #{issue_number}.\n\nInclui o plano de execução em `docs/pr/{issue_number}_feature_plan.md`.'
        ], check=True, timeout=30)
        self.logger.info(f"Pull request criado com sucesso para a issue #{issue_number}")

    def notify_openai_agent_sdk(self, openai_token, issue_number, branch_name):
        self.logger.info("Notificando o Agent SDK da OpenAI...")
        import openai

        client = openai.OpenAI(api_key=openai_token)

        message_content = f"""
        Uma nova feature foi criada:
        - Número da Issue: {issue_number}
        - Nome da branch: {branch_name}
        - Link da PR: https://github.com/{self.repo_owner}/{self.repo_name}/pull/new/{branch_name}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um assistente de monitoramento de fluxo de desenvolvimento."},
                    {"role": "user", "content": message_content}
                ],
                max_tokens=50
            )
            self.logger.info(f"Notificação enviada para o Agent SDK da OpenAI: {response.choices[0].message.content}")
        except Exception as e:
            self.logger.error(f"Falha ao notificar o Agent SDK da OpenAI: {str(e)}")

    def get_git_main_log(self):
        self.logger.info("Obtendo histórico de log da branch main")
        result = subprocess.run(
            ['git', 'log', 'main', '--pretty=format:%h - %s', '-n', '20'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()

    def get_suggestion_from_openai(self, openai_token, prompt_text, git_log):
        import openai
        client = openai.OpenAI(api_key=openai_token)

        suggestion_prompt = f"""
        Considere o seguinte prompt de usuário para criação de feature: "{prompt_text}"
        E o seguinte histórico de commits da branch main:
        {git_log}

        E você pode utilizar ferramentas para:
        - Listar arquivos do projeto
        - Ler conteúdos dos arquivos
        - Obter histórico de commits

        Use essas ferramentas antes de gerar o plano, caso necessário.

        Com base nessas informações, retorne uma resposta JSON contendo os seguintes campos:
        {{
            "branch_type": <feat|fix|docs|chore>,
            "issue_title": "<Título curto da issue>",
            "issue_description": "<Descrição detalhada da issue>",
            "generated_branch_suffix": "<sufixo da branch (slug)>"
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um assistente que retorna respostas no formato JSON sem texto adicional."},
                {"role": "user", "content": suggestion_prompt}
            ],
            max_tokens=500
        )
        content = response.choices[0].message.content
        self.logger.info(f"Sugestão recebida do OpenAI: {content}")
        return json.loads(content)

    def execute_feature_creation(self, prompt_text, execution_plan, openai_token=None):
        self.logger.info("Iniciando processo de criação de feature")
        
        git_log = self.get_git_main_log()
        suggestion = self.get_suggestion_from_openai(openai_token, prompt_text, git_log)

        branch_type = suggestion["branch_type"]
        issue_title = suggestion["issue_title"]
        issue_description = suggestion["issue_description"]
        generated_branch_suffix = suggestion["generated_branch_suffix"]

        issue_number = self.create_github_issue(issue_title, issue_description)

        branch_name = f'{branch_type}/{issue_number}/{generated_branch_suffix}'

        self.create_branch(branch_name)

        self.create_pr_plan_file(issue_number, prompt_text, execution_plan, branch_name)
        self.create_pull_request(branch_name, issue_number)

        if openai_token:
            self.notify_openai_agent_sdk(openai_token, issue_number, branch_name)

        self.logger.info(f"Processo de criação de feature concluído com sucesso para a issue #{issue_number}")
        return issue_number, branch_name
