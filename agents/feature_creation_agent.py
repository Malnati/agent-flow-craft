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
