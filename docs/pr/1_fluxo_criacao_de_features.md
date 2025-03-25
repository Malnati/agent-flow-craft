📜 Plano de execução do fluxo de automação de criação de features

✅ Objetivo

Permitir que o usuário descreva uma nova funcionalidade em forma de prompt, e o agente automatize:
	•	Criação de issue no GitHub
	•	Criação de branch vinculada à issue
	•	Abertura de Pull Request no repositório
	•	Criação automática de um arquivo de PR no diretório `docs/pr` contendo o plano de execução gerado pela IA

⸻

🔎 Etapas do fluxo
1. **Entrada do Prompt:**
   - O usuário fornece um prompt detalhado descrevendo a feature desejada.
2. **Processamento do Prompt:**
   - O agente AutoGen interpreta o prompt, valida sua estrutura e organiza as informações.
3. **Criação da Issue:**
   - Utiliza o GitHub CLI autenticado.
   - Gera título e descrição automaticamente baseados no prompt.
   - Armazena o ID da issue criada para posterior vinculação.
4. **Criação da Branch:**
   - Nomeada seguindo o padrão: `feature/<slug-da-feature>`.
   - Publicação da branch no repositório remoto.
5. **Criação do Arquivo de PR (plano de execução):**
   - O agente cria automaticamente um arquivo Markdown no diretório `docs/pr/`.
   - O arquivo conterá:
     - O prompt original.
     - A interpretação da IA.
     - Um checklist detalhado das etapas planejadas para implementação.
     - Qualquer insight ou consideração adicional extraída do contexto.
   - O nome do arquivo segue o padrão `docs/pr/<issue_number>_descricao_curta.md`.
6. **Abertura do Pull Request:**
   - PR criado automaticamente, vinculado à issue (`Closes #<issue_number>`).
   - O corpo do PR contém um resumo e um link para o plano de execução criado em `docs/pr/`.
7. **Registro de Logs:**
   - Todos os eventos (criação de issue, branch, PR e arquivo de plano) são registrados em `logs/` para rastreabilidade futura.

⸻

⚙ Esqueleto inicial do agente AutoGen

**Arquivo sugerido:** `agents/feature_creation_agent.py`

```python
from autogen import AssistantAgent
import subprocess
import json
import os

class FeatureCreationAgent(AssistantAgent):
    def __init__(self, github_token, repo_owner, repo_name):
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name

    def create_github_issue(self, title, body):
        result = subprocess.run(
            [
                'gh', 'issue', 'create',
                '--repo', f'{self.repo_owner}/{self.repo_name}',
                '--title', title,
                '--body', body,
                '--json', 'number'
            ],
            capture_output=True, text=True, check=True
        )
        issue_data = json.loads(result.stdout)
        return issue_data['number']

    def create_branch(self, branch_name):
        subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
        subprocess.run(['git', 'push', 'origin', branch_name], check=True)

    def create_pr_plan_file(self, issue_number, prompt_text, execution_plan):
        file_name = f'docs/pr/{issue_number}_feature_plan.md'
        with open(file_name, 'w') as f:
            f.write(f'# Plano de execução para a issue #{issue_number}\n\n')
            f.write(f'**Prompt recebido:** {prompt_text}\n\n')
            f.write(f'**Plano de execução gerado pela IA:**\n{execution_plan}\n')
        subprocess.run(['git', 'add', file_name], check=True)
        subprocess.run(['git', 'commit', '-m', f'Add PR plan file for issue #{issue_number}'], check=True)
        subprocess.run(['git', 'push'], check=True)

    def create_pull_request(self, branch_name, issue_number):
        subprocess.run([
            'gh', 'pr', 'create',
            '--base', 'main',
            '--head', branch_name,
            '--title', f'Automated PR for issue #{issue_number}',
            '--body', f'This PR closes issue #{issue_number} and includes the execution plan in `docs/pr/{issue_number}_feature_plan.md`.'
        ], check=True)

    def execute_feature_creation(self, prompt_text, execution_plan):
        issue_title = prompt_text.split('.')[0][:50]
        issue_number = self.create_github_issue(issue_title, prompt_text)
        branch_name = f'feature/issue-{issue_number}'
        self.create_branch(branch_name)
        self.create_pr_plan_file(issue_number, prompt_text, execution_plan)
        self.create_pull_request(branch_name, issue_number)

```
