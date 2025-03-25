from autogen import AssistantAgent
from autogen.tools import tool
import subprocess
import json
import os
import logging
from slugify import slugify
import re

def _list_project_files_internal(directory=".", max_depth=2):
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
def list_project_files():
    return "Esta ferramenta lista arquivos do projeto, disponível apenas via agente."

def _read_project_file_internal(file_path, max_lines=100):
    lines = []
    with open(file_path, 'r') as file:
        for idx, line in enumerate(file):
            if idx >= max_lines:
                break
            lines.append(line)
    return ''.join(lines)

@tool
def read_project_file():
    return "Esta ferramenta lê conteúdos de arquivos, disponível apenas via agente."

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

    def create_pr_plan_file(self, issue_number, prompt_text, execution_plan, branch_name, suggestion=None):
        self.logger.info(f"Criando arquivo de plano para PR da issue #{issue_number}")
        
        file_name = f'docs/pr/{issue_number}_feature_plan.md'
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        
        with open(file_name, 'w') as f:
            f.write(f'# Plano de execução para a issue #{issue_number}\n\n')
            f.write(f'**Prompt recebido:** {prompt_text}\n\n')
            f.write(f'**Plano de execução gerado automaticamente:**\n\n')
            
            if suggestion and 'execution_plan' in suggestion:
                plan = suggestion['execution_plan']
                f.write(f'## Detalhes do Plano\n\n')
                
                # Escrever os entregáveis
                if 'deliverables' in plan:
                    for idx, deliverable in enumerate(plan['deliverables']):
                        f.write(f'### Entregável {idx+1}: {deliverable.get("name", "Sem nome")}\n\n')
                        
                        if 'description' in deliverable:
                            f.write(f'**Descrição:** {deliverable["description"]}\n\n')
                        
                        if 'dependencies' in deliverable:
                            f.write('**Dependências:**\n')
                            for dep in deliverable['dependencies']:
                                f.write(f'- {dep}\n')
                            f.write('\n')
                        
                        if 'usage_example' in deliverable:
                            f.write('**Exemplo de uso:**\n')
                            f.write(f'```\n{deliverable["usage_example"]}\n```\n\n')
                        
                        if 'acceptance_criteria' in deliverable:
                            f.write('**Critérios de aceitação:**\n')
                            for criteria in deliverable['acceptance_criteria']:
                                f.write(f'- {criteria}\n')
                            f.write('\n')
                        
                        if 'troubleshooting' in deliverable:
                            f.write('**Resolução de problemas:**\n')
                            
                            if isinstance(deliverable['troubleshooting'], list):
                                for trouble in deliverable['troubleshooting']:
                                    if isinstance(trouble, dict):
                                        f.write(f'- Problema: {trouble.get("problem", "N/A")}\n')
                                        f.write(f'  - Causa possível: {trouble.get("possible_cause", "N/A")}\n')
                                        f.write(f'  - Resolução: {trouble.get("resolution", "N/A")}\n')
                            elif isinstance(deliverable['troubleshooting'], dict):
                                if 'problem' in deliverable['troubleshooting']:
                                    f.write(f'- Problema: {deliverable["troubleshooting"]["problem"]}\n')
                                    f.write(f'  - Causa possível: {deliverable["troubleshooting"].get("possible_cause", "N/A")}\n')
                                    f.write(f'  - Resolução: {deliverable["troubleshooting"].get("resolution", "N/A")}\n')
                                elif 'possible_causes' in deliverable['troubleshooting'] and 'resolutions' in deliverable['troubleshooting']:
                                    causes = deliverable['troubleshooting']['possible_causes']
                                    resolutions = deliverable['troubleshooting']['resolutions']
                                    for i in range(min(len(causes), len(resolutions))):
                                        f.write(f'- Problema {i+1}:\n')
                                        f.write(f'  - Causa possível: {causes[i]}\n')
                                        f.write(f'  - Resolução: {resolutions[i]}\n')
                            f.write('\n')
                        
                        if 'implementation_steps' in deliverable:
                            f.write('**Passos de implementação:**\n')
                            for idx, step in enumerate(deliverable['implementation_steps']):
                                f.write(f'{idx+1}. {step}\n')
                            f.write('\n')
            else:
                # Se não tiver o plano formatado, usa o texto original
                f.write(f"{execution_plan}\n")
        
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

    def notify_openai_agent_sdk(self, openai_token, issue_number, branch_name, suggestion=None):
        self.logger.info("Notificando o Agent SDK da OpenAI...")
        import openai

        client = openai.OpenAI(api_key=openai_token)

        # Construir mensagem detalhada incluindo os entregáveis do plano
        message_content = f"""
        Uma nova feature foi criada:
        - Número da Issue: {issue_number}
        - Nome da branch: {branch_name}
        - Link da PR: https://github.com/{self.repo_owner}/{self.repo_name}/pull/new/{branch_name}
        """

        if suggestion and 'execution_plan' in suggestion:
            message_content += "\n\nDetalhes do plano de execução:\n"
            
            for idx, deliverable in enumerate(suggestion['execution_plan'].get('deliverables', [])):
                message_content += f"\nEntregável {idx+1}: {deliverable.get('name', 'Sem nome')}\n"
                message_content += f"- Descrição: {deliverable.get('description', 'N/A')}\n"
                
                if 'dependencies' in deliverable:
                    deps = ', '.join(deliverable['dependencies'])
                    message_content += f"- Dependências: {deps}\n"
                
                if 'acceptance_criteria' in deliverable:
                    message_content += "- Critérios de aceitação principais:\n"
                    for i, criteria in enumerate(deliverable['acceptance_criteria'][:3]):  # Limita a 3 critérios
                        message_content += f"  * {criteria}\n"
                
                if 'implementation_steps' in deliverable:
                    message_content += "- Passos principais:\n"
                    for i, step in enumerate(deliverable['implementation_steps'][:3]):  # Limita a 3 passos
                        message_content += f"  * {step}\n"

        message_content += "\n\nPor favor, verifique se o plano de execução está completo e adequado para esta feature. Responda exclusivamente em português."

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um assistente de monitoramento de fluxo de desenvolvimento que analisa planos de execução e sugere melhorias quando necessário. RESPONDA EXCLUSIVAMENTE EM PORTUGUÊS DO BRASIL."},
                    {"role": "user", "content": message_content}
                ],
                max_tokens=150
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

    def get_project_context(self, max_lines=50, max_files=10):
        self.logger.info("Coletando contexto do projeto")
        files = _list_project_files_internal(directory=".", max_depth=2)[:max_files]
        
        if not files:
            raise Exception("Nenhum arquivo encontrado para submissão ao Agent SDK da OpenAI.")

        for file in files:
            try:
                size = os.path.getsize(file)
                self.logger.info(f"Arquivo submetido: {file} (tamanho: {size} bytes)")
            except Exception as e:
                self.logger.warning(f"Não foi possível obter o tamanho do arquivo {file}: {str(e)}")

        context = ""
        for file in files:
            if file.endswith((".py", ".md", ".txt")):
                content = _read_project_file_internal(file, max_lines=max_lines)
                context += f"\n\n### Arquivo: {file}\n```\n{content}\n```"
        return context

    def get_suggestion_from_openai(self, openai_token, prompt_text, git_log):
        import openai
        client = openai.OpenAI(api_key=openai_token)

        project_context = self.get_project_context()

        suggestion_prompt = f"""
Você é um planejador técnico experiente especializado em desenvolvimento de software. Baseado no prompt do usuário abaixo, no histórico de commits e na estrutura de arquivos do projeto, você deve gerar um JSON completo e detalhado.

IMPORTANTE: TODAS AS SUAS RESPOSTAS DEVEM SER EM PORTUGUÊS DO BRASIL. NÃO USE INGLÊS EM NENHUMA PARTE DA SUA RESPOSTA.

Histórico de commits recentes:
{git_log}

Contexto do projeto:
{project_context}

Você deve gerar um JSON completo e detalhado contendo:

{{
  "branch_type": "<feat|fix|docs|chore>", 
  "issue_title": "<Título curto e descritivo da issue em português>",
  "issue_description": "<Descrição detalhada da issue que captura o objetivo e escopo do trabalho em português>",
  "generated_branch_suffix": "<sufixo da branch em formato de slug, sem espaços ou caracteres especiais>",
  "execution_plan": {{
    "deliverables": [
      {{
        "name": "<Nome claro e específico do entregável em português>",
        "description": "<Descrição detalhada do entregável, incluindo seu propósito e funcionalidade em português>",
        "dependencies": ["<lista completa e específica de dependências de código ou externas>"],
        "usage_example": "<exemplo prático e completo de uso do entregável, preferencialmente com código>",
        "acceptance_criteria": ["<lista objetiva e mensurável de critérios específicos de aceite em português>"],
        "troubleshooting": [
          {{
            "problem": "<descrição específica de um possível problema encontrado em português>",
            "possible_cause": "<causa provável e específica do problema em português>",
            "resolution": "<instruções claras e específicas para resolver o problema em português>"
          }}
        ],
        "implementation_steps": [
          "<Passo 1 com instruções detalhadas para implementação em português>",
          "<Passo 2 com instruções detalhadas para implementação em português>",
          "<Passo 3 com instruções detalhadas para implementação em português>"
        ]
      }}
    ]
  }}
}}

O prompt do usuário é:
{prompt_text}

OBSERVAÇÕES IMPORTANTES:
1. Produza uma resposta completa e de alta qualidade com informações específicas, não genéricas.
2. Use exemplos de código reais e apropriados para o contexto do projeto.
3. Forneça dependências específicas com versões (quando aplicável).
4. Inclua critérios de aceitação mensuráveis e verificáveis.
5. Os passos de implementação devem ser detalhados o suficiente para guiar o desenvolvimento.
6. Não use placeholder genéricos como "Descrição breve" ou "Exemplo genérico".
7. Baseie-se no contexto real do projeto e no histórico de commits para criar um plano realista.
8. A resposta deve estar em formato JSON válido sem qualquer texto adicional.
9. TODA A RESPOSTA DEVE SER EM PORTUGUÊS DO BRASIL, INCLUSIVE OS VALORES DOS CAMPOS DO JSON.
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um assistente técnico que gera planos de execução detalhados em formato JSON. Sua resposta deve conter APENAS o JSON sem texto introdutório ou explicativo. VOCÊ DEVE RESPONDER EXCLUSIVAMENTE EM PORTUGUÊS DO BRASIL."},
                {"role": "user", "content": suggestion_prompt}
            ],
            max_tokens=2000,
            temperature=0.2
        )
        content = response.choices[0].message.content

        # Limpa qualquer texto que não seja JSON
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # Verifica se a resposta contém conteúdo genérico
        generic_terms = ["descrição breve", "dependência a", "passo inicial", "exemplo genérico", 
                        "título da issue", "descrição da issue", "nome do entregável", 
                        "lista de dependências", "possível problema"]
        
        if any(term in content.lower() for term in generic_terms):
            self.logger.warning("Resposta genérica detectada, solicitando nova sugestão.")
            return self.get_suggestion_from_openai(openai_token, prompt_text, git_log)

        try:
            json_content = json.loads(content)
            # Verifica se execution_plan e deliverables existem
            if 'execution_plan' not in json_content or 'deliverables' not in json_content['execution_plan'] or not json_content['execution_plan']['deliverables']:
                self.logger.warning("Resposta sem plano de execução ou entregáveis, solicitando nova sugestão.")
                return self.get_suggestion_from_openai(openai_token, prompt_text, git_log)
            
            self.logger.info(f"Sugestão recebida do OpenAI: {content}")
            return json_content
        except json.JSONDecodeError:
            self.logger.error("Falha ao decodificar JSON da resposta da OpenAI.")
            # Tenta novamente com uma nova solicitação
            return self.get_suggestion_from_openai(openai_token, prompt_text, git_log)

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

        self.create_pr_plan_file(issue_number, prompt_text, execution_plan, branch_name, suggestion)
        self.create_pull_request(branch_name, issue_number)

        if openai_token:
            self.notify_openai_agent_sdk(openai_token, issue_number, branch_name, suggestion)

        self.logger.info(f"Processo de criação de feature concluído com sucesso para a issue #{issue_number}")
        return issue_number, branch_name
