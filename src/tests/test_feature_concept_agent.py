import unittest
import os
import json
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Adicionar o diretório raiz ao sys.path para importações relativas corretas
sys.path.insert(0, str(Path(__file__).parent.parent))

from apps.agent_manager.agents.feature_concept_agent import FeatureConceptAgent

class TestFeatureConceptAgent(unittest.TestCase):
    """Testes para o FeatureConceptAgent"""
    
    def setUp(self):
        """Configura ambiente para testes."""
        # Criar diretório de testes temporário
        self.test_dir = Path("test_context")
        self.test_dir.mkdir(exist_ok=True)
        
        # Criar agente de teste com token mockado
        self.agent = FeatureConceptAgent(openai_token="test_token")
        self.agent.context_dir = self.test_dir
    
    def tearDown(self):
        """Limpa após testes."""
        # Remover arquivos de teste
        for file in self.test_dir.glob("*.json"):
            file.unlink()
        
        # Remover diretório de teste
        if self.test_dir.exists():
            self.test_dir.rmdir()
    
    def test_initialization(self):
        """Testa inicialização básica do agente."""
        agent = FeatureConceptAgent(openai_token="test_token")
        self.assertEqual(agent.model, "gpt-4")  # Modelo padrão
        self.assertEqual(agent.openai_token, "test_token")
    
    def test_set_model(self):
        """Testa mudança de modelo."""
        result = self.agent.set_model("gpt-3.5-turbo")
        self.assertEqual(result, "gpt-3.5-turbo")
        self.assertEqual(self.agent.model, "gpt-3.5-turbo")
    
    @patch("apps.agent_manager.agents.feature_concept_agent.OpenAI")
    def test_process_concept(self, mock_openai):
        """Testa processamento de conceito quando OpenAI responde corretamente."""
        # Criar um conceito de teste no diretório de contexto
        concept_id = "concept_20240415_123456"
        test_concept = {
            "concept_summary": "Sistema de autenticação",
            "concept_description": "Implementar sistema de login",
            "key_goals": ["Autenticar usuários", "Proteger rotas"],
            "possible_approaches": ["JWT", "OAuth", "Session"],
            "considerations": ["Segurança", "Performance"]
        }
        
        concept_data = {
            "id": concept_id,
            "type": "concept", 
            "timestamp": "20240415_123456",
            "prompt": "Implementar sistema de autenticação",
            "concept": test_concept,
            "status": "success"
        }
        
        # Salvar o conceito no diretório de teste
        with open(self.test_dir / f"{concept_id}.json", "w") as f:
            json.dump(concept_data, f)
        
        # Mock da resposta da OpenAI
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = json.dumps({
            "branch_type": "feat",
            "issue_title": "Implementar sistema de autenticação com JWT",
            "issue_description": "Adicionar autenticação via JWT",
            "generated_branch_suffix": "auth-system",
            "execution_plan": {
                "steps": ["Passo 1", "Passo 2"],
                "estimated_complexity": "média",
                "estimated_hours": "8",
                "technical_details": "Detalhes técnicos",
                "dependencies": ["jsonwebtoken"],
                "affected_components": ["auth", "api"]
            }
        })
        mock_response.choices = [MagicMock(message=mock_message)]
        
        # Configurar o mock do cliente OpenAI
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Executar o método
        result = self.agent.process_concept(concept_id)
        
        # Verificar se o método OpenAI foi chamado
        mock_client.chat.completions.create.assert_called_once()
        
        # Verificar resultado
        self.assertIn("branch_type", result)
        self.assertIn("issue_title", result) 
        self.assertIn("issue_description", result)
        self.assertIn("generated_branch_suffix", result)
        self.assertIn("execution_plan", result)
        self.assertIn("context_id", result)
        self.assertEqual(result["execution_plan"]["estimated_complexity"], "média")
        
        # Verificar se o arquivo de contexto foi gerado
        feature_concept_id = result["context_id"]
        feature_concept_file = self.test_dir / f"{feature_concept_id}.json"
        self.assertTrue(feature_concept_file.exists())
        
        # Verificar conteúdo do arquivo
        with open(feature_concept_file, "r") as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data["type"], "feature_concept")
        self.assertEqual(saved_data["original_concept_id"], concept_id)
    
    def test_default_feature_concept(self):
        """Testa criação de feature concept padrão."""
        original_concept = {
            "concept_summary": "Sistema de login",
            "concept_description": "Implementar sistema básico"
        }
        prompt = "Sistema de login"
        
        result = self.agent._create_default_feature_concept(original_concept, prompt)
        
        self.assertIn("branch_type", result)
        self.assertIn("issue_title", result)
        self.assertIn("issue_description", result)
        self.assertIn("generated_branch_suffix", result)
        self.assertIn("execution_plan", result)
        
        self.assertEqual(result["branch_type"], "feat")
        self.assertEqual(result["issue_title"], "Feature: Sistema de login")

if __name__ == "__main__":
    unittest.main() 