"""
Teste das operações de arquivo com backup e limpeza de diretórios vazios do RefactorAgent.
"""
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from apps.agent_manager.agents.refactor_agent import RefactorAgent


class TestRefactorFileOperations(unittest.TestCase):
    """Testes para operações de arquivo do RefactorAgent."""
    
    def setUp(self):
        """Configura o ambiente de teste."""
        # Criar diretório temporário para o teste
        self.test_dir = tempfile.mkdtemp()
        
        # Estrutura de diretórios para teste
        self.src_dir = os.path.join(self.test_dir, "src")
        self.utils_dir = os.path.join(self.src_dir, "utils")
        self.components_dir = os.path.join(self.src_dir, "components")
        self.ui_dir = os.path.join(self.components_dir, "ui")
        
        # Criar estrutura
        os.makedirs(self.utils_dir, exist_ok=True)
        os.makedirs(self.components_dir, exist_ok=True)
        
        # Criar arquivos de teste
        self.utils_file = os.path.join(self.utils_dir, "helpers.py")
        self.component_file = os.path.join(self.components_dir, "button.py")
        
        # Criar conteúdo de teste
        with open(self.utils_file, "w") as f:
            f.write("# Arquivo de utilitários para teste\n\ndef helper_function():\n    return 'helper'")
        
        with open(self.component_file, "w") as f:
            f.write("# Componente de botão para teste\n\nclass Button:\n    def render(self):\n        return '<button>'")
        
        # Inicializar o agente
        self.agent = RefactorAgent(
            project_dir=self.test_dir,
            dry_run=False
        )
    
    def tearDown(self):
        """Limpa o ambiente após o teste."""
        # Remover diretório temporário
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_move_with_backup(self):
        """Testa movimentação de arquivo com backup."""
        # Configurar novo caminho
        os.makedirs(self.ui_dir, exist_ok=True)
        new_path = os.path.join(self.ui_dir, "button.py")
        
        # Executar movimentação
        success = self.agent.move_with_backup(self.component_file, new_path)
        
        # Verificar resultado
        self.assertTrue(success, "A operação de movimentação falhou")
        self.assertTrue(os.path.exists(new_path), "O arquivo não foi movido para o novo local")
        
        # Verificar backup
        backup_dir = os.path.join(self.test_dir, "bak")
        backup_file = os.path.join(backup_dir, "src", "components", "button.py")
        self.assertTrue(os.path.exists(backup_dir), "Diretório de backup não foi criado")
        self.assertTrue(os.path.exists(backup_file), "Arquivo de backup não foi criado")
        
        # Verificar conteúdo do backup
        with open(backup_file, "r") as f:
            backup_content = f.read()
        
        self.assertIn("Componente de botão para teste", backup_content, 
                      "O conteúdo do backup não corresponde ao original")
    
    def test_cleanup_empty_dirs(self):
        """Testa limpeza de diretórios vazios após movimentação."""
        # Criar diretório adicional para teste
        empty_dir = os.path.join(self.utils_dir, "empty")
        os.makedirs(empty_dir, exist_ok=True)
        
        # Mover único arquivo do diretório utils
        new_dir = os.path.join(self.test_dir, "helpers")
        os.makedirs(new_dir, exist_ok=True)
        new_path = os.path.join(new_dir, "utils.py")
        
        # Executar movimentação
        success = self.agent.move_with_backup(self.utils_file, new_path)
        
        # Verificar resultado
        self.assertTrue(success, "A operação de movimentação falhou")
        self.assertFalse(os.path.exists(self.utils_dir), 
                         "Diretório utils não foi removido após ficar vazio")
        self.assertFalse(os.path.exists(empty_dir), 
                         "Subdiretório vazio não foi removido")
    
    def test_rename_file(self):
        """Testa renomeação de arquivo."""
        # Novo nome para o arquivo
        new_name = os.path.join(self.utils_dir, "utility_helpers.py")
        
        # Executar renomeação
        success = self.agent.rename_file(self.utils_file, new_name)
        
        # Verificar resultado
        self.assertTrue(success, "A operação de renomeação falhou")
        self.assertTrue(os.path.exists(new_name), "O arquivo não foi renomeado corretamente")
        self.assertFalse(os.path.exists(self.utils_file), "O arquivo original não foi removido")
        
        # Verificar backup
        backup_dir = os.path.join(self.test_dir, "bak")
        backup_file = os.path.join(backup_dir, "src", "utils", "helpers.py")
        self.assertTrue(os.path.exists(backup_file), "Arquivo de backup não foi criado")


if __name__ == "__main__":
    unittest.main() 