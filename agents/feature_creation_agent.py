from autogen import AssistantAgent
import subprocess
import json
import os
import logging
import re

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
            f.write(f'**Plano de execução gerado pela IA:**\n{execution_plan}\n')
        
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
            '--body', f'This PR closes issue #{issue_number} and includes the execution plan in `docs/pr/{issue_number}_feature_plan.md`.'
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

        Com base nessas informações, sugira:
        1. O tipo da branch (feat, fix, docs ou chore)
        2. Um título curto (até 50 caracteres) para a issue
        3. Uma descrição detalhada para a issue
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um assistente que auxilia a nomear branches, títulos e descrições de issues baseado no histórico do repositório e solicitações do usuário."},
                {"role": "user", "content": suggestion_prompt}
            ],
            max_tokens=500
        )
        content = response.choices[0].message.content
        self.logger.info(f"Sugestão recebida do OpenAI: {content}")
        return content

    def execute_feature_creation(self, prompt_text, execution_plan, openai_token=None):
        self.logger.info("Iniciando processo de criação de feature")
        
        git_log = self.get_git_main_log()
        suggestion = self.get_suggestion_from_openai(openai_token, prompt_text, git_log)
        # parse suggestion aqui (usuário fará manualmente ou em próxima etapa)

        issue_title = prompt_text.split('.')[0][:50]
        self.logger.info(f"Título da issue: {issue_title}")
        
        issue_number = self.create_github_issue(issue_title, prompt_text)
        
        # Detectar tipo de branch automaticamente a partir do plano de execução
        if any(keyword in execution_plan.lower() for keyword in ["corrigir", "correção", "bug", "fix"]):
            branch_type = "fix"
        elif any(keyword in execution_plan.lower() for keyword in ["documentação", "docs"]):
            branch_type = "docs"
        elif any(keyword in execution_plan.lower() for keyword in ["chore", "infraestrutura", "ajuste", "infra"]):
            branch_type = "chore"
        else:
            branch_type = "feat"

        generated_branch_suffix = execution_plan.replace(" ", "-").lower()[:30]
        branch_name = f'{branch_type}/{issue_number}/{generated_branch_suffix}'
        
        self.create_branch(branch_name)

        self.create_pr_plan_file(issue_number, prompt_text, execution_plan, branch_name)
        self.create_pull_request(branch_name, issue_number)

        if openai_token:
            self.notify_openai_agent_sdk(openai_token, issue_number, branch_name)

        self.logger.info(f"Processo de criação de feature concluído com sucesso para a issue #{issue_number}")
        return issue_number, branch_name
