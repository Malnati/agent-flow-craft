import unittest
from unittest.mock import patch, MagicMock
import logging
import os
import time
from agents.feature_creation_agent import FeatureCreationAgent

class TestFeatureCreationAgent(unittest.TestCase):

    def setUp(self):
        # Configurar o logger para os testes
        self.logger_mock = MagicMock(spec=logging.Logger)
        logging.getLogger = MagicMock(return_value=self.logger_mock)
        
        # Mockando time.sleep para não atrasar os testes
        self.sleep_patcher = patch('time.sleep')
        self.mock_sleep = self.sleep_patcher.start()
        
        # Mockando os.makedirs para não criar diretórios durante os testes
        self.makedirs_patcher = patch('os.makedirs')
        self.mock_makedirs = self.makedirs_patcher.start()

    def tearDown(self):
        self.sleep_patcher.stop()
        self.makedirs_patcher.stop()

    @patch('subprocess.run')
    def test_create_github_issue(self, mock_run):
        mock_run.return_value.stdout = '{"number": 123}'
        agent = FeatureCreationAgent('token', 'owner', 'repo')
        issue_number = agent.create_github_issue('Test Issue', 'This is a test issue.')
        self.assertEqual(issue_number, 123)
        mock_run.assert_called_once()
        
        # Verificar se os logs foram chamados
        self.logger_mock.info.assert_any_call("Criando issue: Test Issue")
        self.logger_mock.info.assert_any_call("Issue #123 criada com sucesso")
        
        # Verificar se o timeout foi chamado
        self.mock_sleep.assert_called_with(1)

    @patch('subprocess.run')
    def test_create_branch(self, mock_run):
        agent = FeatureCreationAgent('token', 'owner', 'repo')
        agent.create_branch('feature/test-branch')
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_any_call(['git', 'checkout', '-b', 'feature/test-branch'], check=True)
        mock_run.assert_any_call(['git', 'push', 'origin', 'feature/test-branch'], check=True)
        
        # Verificar se os logs foram chamados
        self.logger_mock.info.assert_any_call("Criando branch: feature/test-branch")
        self.logger_mock.info.assert_any_call("Branch feature/test-branch criada e enviada para o repositório remoto")
        
        # Verificar se os timeouts foram chamados
        self.assertEqual(self.mock_sleep.call_count, 2)

    @patch('subprocess.run')
    def test_create_pr_plan_file(self, mock_run):
        # Mock para open
        open_mock = unittest.mock.mock_open()
        with patch('builtins.open', open_mock):
            agent = FeatureCreationAgent('token', 'owner', 'repo')
            agent.create_pr_plan_file(123, 'Test prompt', 'Test execution plan')
            
        self.assertEqual(mock_run.call_count, 3)
        mock_run.assert_any_call(['git', 'add', 'docs/pr/123_feature_plan.md'], check=True)
        mock_run.assert_any_call(['git', 'commit', '-m', 'Add PR plan file for issue #123'], check=True)
        mock_run.assert_any_call(['git', 'push'], check=True)
        
        # Verificar se os logs foram chamados
        self.logger_mock.info.assert_any_call("Criando arquivo de plano para PR da issue #123")
        self.logger_mock.info.assert_any_call("Arquivo de plano de PR criado e enviado para o repositório remoto")
        
        # Verificar se os diretórios foram criados
        self.mock_makedirs.assert_called_once_with(os.path.dirname('docs/pr/123_feature_plan.md'), exist_ok=True)
        
        # Verificar se os timeouts foram chamados
        self.assertEqual(self.mock_sleep.call_count, 3)

    @patch('subprocess.run')
    def test_create_pull_request(self, mock_run):
        agent = FeatureCreationAgent('token', 'owner', 'repo')
        agent.create_pull_request('feature/test-branch', 123)
        mock_run.assert_called_once_with([
            'gh', 'pr', 'create',
            '--base', 'main',
            '--head', 'feature/test-branch',
            '--title', f'Automated PR for issue #123',
            '--body', f'This PR closes issue #123 and includes the execution plan in `docs/pr/123_feature_plan.md`.'
        ], check=True)
        
        # Verificar se os logs foram chamados
        self.logger_mock.info.assert_any_call("Criando pull request para a issue #123 da branch feature/test-branch")
        self.logger_mock.info.assert_any_call("Pull request criado com sucesso para a issue #123")
        
        # Verificar se o timeout foi chamado
        self.mock_sleep.assert_called_with(1)

    @patch.object(FeatureCreationAgent, 'create_github_issue', return_value=123)
    @patch.object(FeatureCreationAgent, 'create_branch')
    @patch.object(FeatureCreationAgent, 'create_pr_plan_file')
    @patch.object(FeatureCreationAgent, 'create_pull_request')
    def test_execute_feature_creation(self, mock_create_pull_request, mock_create_pr_plan_file, mock_create_branch, mock_create_github_issue):
        agent = FeatureCreationAgent('token', 'owner', 'repo')
        issue_number, branch_name = agent.execute_feature_creation('Test prompt', 'Test execution plan')
        
        self.assertEqual(issue_number, 123)
        self.assertEqual(branch_name, 'feature/issue-123')
        
        mock_create_github_issue.assert_called_once_with('Test prompt', 'Test prompt')
        mock_create_branch.assert_called_once_with('feature/issue-123')
        mock_create_pr_plan_file.assert_called_once_with(123, 'Test prompt', 'Test execution plan')
        mock_create_pull_request.assert_called_once_with('feature/issue-123', 123)
        
        # Verificar se os logs foram chamados
        self.logger_mock.info.assert_any_call("Iniciando processo de criação de feature")
        self.logger_mock.info.assert_any_call("Título da issue: Test prompt")
        self.logger_mock.info.assert_any_call("Processo de criação de feature concluído com sucesso para a issue #123")

if __name__ == '__main__':
    unittest.main()
