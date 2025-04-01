import unittest
from unittest.mock import patch, MagicMock
import logging
import os
import subprocess
from agents.agent_feature_creation import FeatureCreationAgent
from core.logger import get_logger, log_execution
from pathlib import Path

logger = get_logger(__name__)

# Configurar cache do pytest
os.environ.setdefault("PYTHONPYCACHEPREFIX", str(Path().absolute() / "out"))

class TestFeatureCreationAgent(unittest.TestCase):

    def setUp(self):
        logger.info("INÍCIO - setUp | Configurando ambiente de teste")
        self.logger_mock = MagicMock(spec=logging.Logger)
        logging.getLogger = MagicMock(return_value=self.logger_mock)
        
        # Mockando os.makedirs para não criar diretórios durante os testes
        self.makedirs_patcher = patch('os.makedirs')
        self.mock_makedirs = self.makedirs_patcher.start()
        
        # Patch para o método check_github_auth
        self.auth_patcher = patch.object(FeatureCreationAgent, 'check_github_auth')
        self.mock_auth = self.auth_patcher.start()
        logger.info("SUCESSO - Ambiente de teste configurado")

    def tearDown(self):
        logger.info("INÍCIO - tearDown | Limpando ambiente de teste")
        self.makedirs_patcher.stop()
        self.auth_patcher.stop()
        logger.info("SUCESSO - Ambiente de teste limpo")

    @log_execution
    @patch('subprocess.run')
    def test_create_github_issue(self, mock_run):
        """Testa a criação de issues no GitHub"""
        logger.info("INÍCIO - test_create_github_issue")
        
        try:
            mock_run.return_value.stdout = 'https://github.com/owner/repo/issues/123\n'
            agent = FeatureCreationAgent('token', 'owner', 'repo')
            
            # Reset o mock para ignorar a chamada do check_github_auth
            mock_run.reset_mock()
            
            issue_number = agent.create_github_issue('Test Issue', 'Test body')
            
            self.assertEqual(issue_number, 123)
            mock_run.assert_called_once()
            
            # Verificar se os logs foram chamados
            self.logger_mock.info.assert_any_call("Criando issue: Test Issue")
            self.logger_mock.info.assert_any_call("Issue #123 criada e capturada com sucesso")
            logger.info("SUCESSO - Teste de criação de issue concluído")
        except Exception as e:
            logger.error(f"FALHA - test_create_github_issue | Erro: {str(e)}", exc_info=True)
            raise

    @patch('subprocess.run')
    def test_create_branch(self, mock_run):
        agent = FeatureCreationAgent('token', 'owner', 'repo')
        
        # Reset o mock para ignorar a chamada do check_github_auth
        mock_run.reset_mock()
        
        agent.create_branch('feature/test-branch')
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_any_call(['git', 'checkout', '-b', 'feature/test-branch'], check=True, timeout=30)
        mock_run.assert_any_call(['git', 'push', '--set-upstream', 'origin', 'feature/test-branch'], check=True, timeout=30)
        
        # Verificar se os logs foram chamados
        self.logger_mock.info.assert_any_call("Criando branch: feature/test-branch")
        self.logger_mock.info.assert_any_call("Branch feature/test-branch criada e enviada para o repositório remoto")

    @patch('subprocess.run')
    def test_create_pr_plan_file(self, mock_run):
        # Mock para open
        open_mock = unittest.mock.mock_open()
        with patch('builtins.open', open_mock):
            agent = FeatureCreationAgent('token', 'owner', 'repo')
            
            # Reset o mock para ignorar a chamada do check_github_auth
            mock_run.reset_mock()
            
            agent.create_pr_plan_file(123, 'Test prompt', 'Test execution plan', 'feature/test-branch')
            
        self.assertEqual(mock_run.call_count, 3)
        mock_run.assert_any_call(['git', 'add', 'docs/pr/123_feature_plan.md'], check=True, timeout=30)
        mock_run.assert_any_call(['git', 'commit', '-m', 'Add PR plan file for issue #123'], check=True, timeout=30)
        mock_run.assert_any_call(['git', 'push'], check=True, timeout=30)
        
        # Verificar se os logs foram chamados
        self.logger_mock.info.assert_any_call("Criando arquivo de plano para PR da issue #123")
        self.logger_mock.info.assert_any_call("Arquivo de plano de PR criado e enviado para o repositório remoto")
        
        # Verificar se os diretórios foram criados
        self.mock_makedirs.assert_called_once_with(os.path.dirname('docs/pr/123_feature_plan.md'), exist_ok=True)

    @patch('subprocess.run')
    def test_create_pull_request(self, mock_run):
        agent = FeatureCreationAgent('token', 'owner', 'repo')
        
        # Reset o mock para ignorar a chamada do check_github_auth
        mock_run.reset_mock()
        
        agent.create_pull_request('feature/test-branch', 123)
        mock_run.assert_called_once_with([
            'gh', 'pr', 'create',
            '--base', 'main',
            '--head', 'feature/test-branch',
            '--title', f'Automated PR for issue #123',
            '--body', f'This PR closes issue #123 and includes the execution plan in `docs/pr/123_feature_plan.md`.'
        ], check=True, timeout=30)
        
        # Verificar se os logs foram chamados
        self.logger_mock.info.assert_any_call("Criando pull request para a issue #123 da branch feature/test-branch")
        self.logger_mock.info.assert_any_call("Pull request criado com sucesso para a issue #123")

    @patch.object(FeatureCreationAgent, 'get_suggestion_from_openai')
    @patch.object(FeatureCreationAgent, 'create_github_issue', return_value=123)
    @patch.object(FeatureCreationAgent, 'create_branch')
    @patch.object(FeatureCreationAgent, 'create_pr_plan_file')
    @patch.object(FeatureCreationAgent, 'create_pull_request')
    def test_execute_feature_creation(self, mock_create_pull_request, mock_create_pr_plan_file, mock_create_branch, mock_create_github_issue, mock_openai_suggestion):
        mock_openai_suggestion.return_value = {
            'branch_type': 'feat',
            'issue_title': 'Test Issue Title',
            'issue_description': 'Test Issue Description',
            'generated_branch_suffix': 'test-branch-suffix'
        }
        agent = FeatureCreationAgent('token', 'owner', 'repo')
        issue_number, branch_name = agent.execute_feature_creation('Test prompt', 'Test execution plan', 'fake_openai_token')
        
        self.assertEqual(issue_number, 123)
        self.assertEqual(branch_name, 'feat/123/test-branch-suffix')
        
        mock_create_github_issue.assert_called_once_with('Test Issue Title', 'Test Issue Description')
        mock_create_branch.assert_called_once_with('feat/123/test-branch-suffix')
        mock_create_pr_plan_file.assert_called_once_with(123, 'Test prompt', 'Test execution plan', 'feat/123/test-branch-suffix')
        mock_create_pull_request.assert_called_once_with('feat/123/test-branch-suffix', 123)
        
        # Verificar se os logs foram chamados
        self.logger_mock.info.assert_any_call("Processo de criação de feature concluído com sucesso para a issue #123")

    @patch('subprocess.run')
    def test_check_github_auth(self, mock_run):
        agent = FeatureCreationAgent('token', 'owner', 'repo')
        
        # Como o método check_github_auth já foi chamado no __init__, vamos redefini-lo
        # e depois chamar novamente para testar
        self.auth_patcher.stop()
        
        mock_run.reset_mock()
        mock_run.return_value.returncode = 0
        
        agent.check_github_auth()
        
        mock_run.assert_called_once_with(['gh', 'auth', 'status'], check=True, capture_output=True, timeout=15)
        self.logger_mock.info.assert_any_call("Verificando autenticação do GitHub CLI...")
        self.logger_mock.info.assert_any_call("Autenticação do GitHub verificada com sucesso.")
        
        # Reinicia o patch para não afetar outros testes
        self.auth_patcher = patch.object(FeatureCreationAgent, 'check_github_auth')
        self.mock_auth = self.auth_patcher.start()

    @patch('subprocess.run')
    def test_check_github_auth_failure(self, mock_run):
        agent = FeatureCreationAgent('token', 'owner', 'repo')
        
        # Como o método check_github_auth já foi chamado no __init__, vamos redefini-lo
        # e depois chamar novamente para testar
        self.auth_patcher.stop()
        
        mock_run.reset_mock()
        # Simular falha na autenticação
        mock_run.side_effect = subprocess.CalledProcessError(1, ['gh', 'auth', 'status'])
        
        # Verificar se a exceção é lançada
        with self.assertRaises(subprocess.CalledProcessError):
            agent.check_github_auth()
        
        mock_run.assert_called_once_with(['gh', 'auth', 'status'], check=True, capture_output=True, timeout=15)
        self.logger_mock.info.assert_any_call("Verificando autenticação do GitHub CLI...")
        self.logger_mock.error.assert_called_once_with("Falha na autenticação do GitHub CLI. Execute 'gh auth login' para autenticar.")
        
        # Reinicia o patch para não afetar outros testes
        self.auth_patcher = patch.object(FeatureCreationAgent, 'check_github_auth')
        self.mock_auth = self.auth_patcher.start()

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()
