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

⸻

## 📝 Prompt completo sugerido para o agente

> Abaixo segue o prompt ideal a ser utilizado pelo agente de IA para executar automaticamente o fluxo de criação de features, passo a passo, do início ao fim:

---

**Prompt:**

Você é um agente responsável por automatizar o fluxo de criação de novas funcionalidades neste projeto. Siga cuidadosamente as etapas abaixo e registre todas as ações:

1. Receba a descrição de uma nova funcionalidade em linguagem natural (prompt do usuário).
2. Gere um título resumido e uma descrição estruturada para a issue a partir do prompt.
3. Crie uma issue no repositório usando o GitHub CLI, contendo:
   - Título resumido.
   - Descrição completa com o prompt original, justificativas, contexto, proposta e impacto esperado.
   - Checklist básico com as etapas de execução previstas.
4. Capture automaticamente o número da issue criada a partir da resposta do CLI.
5. Crie uma branch local utilizando o padrão `feature/issue-<issue_number>`.
6. Faça push da branch para o repositório remoto.
7. Gere automaticamente um plano de execução detalhado para a feature com base no prompt, incluindo:
   - Contexto.
   - Descrição da solução.
   - Alternativas consideradas.
   - Checklist técnico de implementação.
   - Observações e considerações do agente.
8. Salve o plano de execução em um arquivo Markdown dentro de `docs/pr/` com o nome `<issue_number>_feature_plan.md`.
9. Faça commit e push desse arquivo para o repositório.
10. Crie um Pull Request utilizando o GitHub CLI, vinculado à issue criada (com `Closes #<issue_number>`), incluindo:
    - Um resumo da feature.
    - Um link direto para o plano de execução no diretório `docs/pr/`.
    - Um checklist de validação.
11. Confirme que o PR foi criado corretamente e registre tudo no log de execução.
12. Informe o usuário de que o processo foi concluído, exibindo a URL da issue e da PR criadas.

---
