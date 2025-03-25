import unittest
from unittest.mock import patch, MagicMock
from agents.feature_creation_agent import FeatureCreationAgent

class TestFeatureCreationAgent(unittest.TestCase):

    @patch('subprocess.run')
    def test_create_github_issue(self, mock_run):
        mock_run.return_value.stdout = '{"number": 123}'
        agent = FeatureCreationAgent('token', 'owner', 'repo')
        issue_number = agent.create_github_issue('Test Issue', 'This is a test issue.')
        self.assertEqual(issue_number, 123)
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_create_branch(self, mock_run):
        agent = FeatureCreationAgent('token', 'owner', 'repo')
        agent.create_branch('feature/test-branch')
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_any_call(['git', 'checkout', '-b', 'feature/test-branch'], check=True)
        mock_run.assert_any_call(['git', 'push', 'origin', 'feature/test-branch'], check=True)

    @patch('subprocess.run')
    def test_create_pr_plan_file(self, mock_run):
        agent = FeatureCreationAgent('token', 'owner', 'repo')
        agent.create_pr_plan_file(123, 'Test prompt', 'Test execution plan')
        self.assertEqual(mock_run.call_count, 3)
        mock_run.assert_any_call(['git', 'add', 'docs/pr/123_feature_plan.md'], check=True)
        mock_run.assert_any_call(['git', 'commit', '-m', 'Add PR plan file for issue #123'], check=True)
        mock_run.assert_any_call(['git', 'push'], check=True)

    @patch('subprocess.run')
    def test_create_pull_request(self, mock_run):
        agent = FeatureCreationAgent('token', 'owner', 'repo')
        agent.create_pull_request('feature/test-branch', 123)
        mock_run.assert_called_once_with([
            'gh', 'pr', 'create',
            '--base', 'main',
            '--head', 'feature/test-branch',
            '--title', 'Automated PR for issue #123',
            '--body', 'This PR closes issue #123 and includes the execution plan in `docs/pr/123_feature_plan.md`.'
        ], check=True)

    @patch.object(FeatureCreationAgent, 'create_github_issue', return_value=123)
    @patch.object(FeatureCreationAgent, 'create_branch')
    @patch.object(FeatureCreationAgent, 'create_pr_plan_file')
    @patch.object(FeatureCreationAgent, 'create_pull_request')
    def test_execute_feature_creation(self, mock_create_pull_request, mock_create_pr_plan_file, mock_create_branch, mock_create_github_issue):
        agent = FeatureCreationAgent('token', 'owner', 'repo')
        agent.execute_feature_creation('Test prompt', 'Test execution plan')
        mock_create_github_issue.assert_called_once_with('Test prompt', 'Test prompt')
        mock_create_branch.assert_called_once_with('feature/issue-123')
        mock_create_pr_plan_file.assert_called_once_with(123, 'Test prompt', 'Test execution plan')
        mock_create_pull_request.assert_called_once_with('feature/issue-123', 123)

if __name__ == '__main__':
    unittest.main()
