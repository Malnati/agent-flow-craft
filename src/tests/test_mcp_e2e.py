#!/usr/bin/env python3
"""
Teste e2e para o MCP (Message Control Protocol)
Executa um make deploy e depois usa o MCP para criar uma nova feature
"""
import unittest
import os
import json
import subprocess
import logging
import tempfile
import time
import uuid
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger('test_mcp_e2e')

class TestMCPE2E(unittest.TestCase):
    """Testes end-to-end para o MCP"""
    
    def setUp(self):
        """Configuração do ambiente de teste"""
        logger.info("INÍCIO - setUp | Configurando ambiente de teste")
        # Verificar se as variáveis de ambiente necessárias estão definidas
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.github_owner = os.environ.get('GITHUB_OWNER')
        self.github_repo = os.environ.get('GITHUB_REPO')
        self.openai_token = os.environ.get('OPENAI_API_KEY')
        
        # Diretório temporário para o teste
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"Diretório temporário criado: {self.temp_dir}")
        logger.info("SUCESSO - Ambiente de teste configurado")

    def tearDown(self):
        """Limpeza do ambiente de teste"""
        logger.info("INÍCIO - tearDown | Limpando ambiente de teste")
        # Se necessário, remover arquivos temporários
        logger.info("SUCESSO - Ambiente de teste limpo")
    
    def test_mcp_feature_creation(self):
        """Teste completo que executa make deploy e depois usa o MCP para criar uma feature"""
        try:
            logger.info("INÍCIO - test_mcp_feature_creation")
            
            # Etapa 1: Executar make deploy
            logger.info("Executando 'make deploy'...")
            deploy_result = subprocess.run(
                ['make', 'deploy'],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info("Deploy concluído com sucesso!")
            logger.debug(f"Saída do deploy: {deploy_result.stdout}")
            
            # Etapa 2: Configurar comunicação com o MCP
            logger.info("Configurando comunicação com o MCP...")
            
            # Nome único para a nova feature
            feature_name = f"feature-test-{uuid.uuid4().hex[:8]}"
            prompt = f"Test feature: {feature_name}"
            execution_plan = "Plano de execução detalhado para teste"
            
            # Criar mensagem para o MCP
            message = {
                "message_id": str(uuid.uuid4()),
                "command": "create_feature",
                "payload": {
                    "prompt": prompt
                }
            }
            
            # Criar arquivo temporário com a mensagem
            message_file = os.path.join(self.temp_dir, "message.json")
            with open(message_file, 'w') as f:
                json.dump(message, f)
            
            # Configurar variáveis de ambiente para o MCP
            env = os.environ.copy()
            env['GITHUB_TOKEN'] = self.github_token
            env['GITHUB_OWNER'] = self.github_owner
            env['GITHUB_REPO'] = self.github_repo
            env['OPENAI_API_KEY'] = self.openai_token
            
            # Etapa 3: Iniciar o MCP e enviar mensagem
            logger.info("Iniciando o MCP e enviando mensagem...")
            
            # Localizar o executável mcp_agent
            home_dir = os.path.expanduser("~")
            mcp_agent_path = os.path.join(home_dir, ".cursor", "mcp_agent.py")
            
            # Verificar se o arquivo existe
            if not os.path.exists(mcp_agent_path):
                logger.error(f"Arquivo MCP Agent não encontrado em: {mcp_agent_path}")
                # Tentar encontrar em outro local
                mcp_agent_path = "./src/scripts/mcp_agent.py"
                if not os.path.exists(mcp_agent_path):
                    self.fail(f"MCP Agent não encontrado")
            
            # Processo MCP
            with open(message_file, 'r') as input_file:
                mcp_process = subprocess.Popen(
                    [mcp_agent_path],
                    stdin=input_file,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    text=True
                )
                
                # Esperar pela resposta
                stdout, stderr = mcp_process.communicate(timeout=30)
                
                # Verificar sucesso
                self.assertEqual(0, mcp_process.returncode, f"MCP falhou com erro: {stderr}")
                
                # Analisar resposta
                try:
                    response = json.loads(stdout)
                    logger.info(f"Resposta recebida: {json.dumps(response)[:100]}...")
                    
                    # Verificar se a resposta é válida
                    self.assertEqual("success", response.get("status"), 
                                    f"Falha no MCP: {response.get('error', 'Erro desconhecido')}")
                    
                    # Verificar se contém os dados esperados
                    result = response.get("result", {})
                    self.assertIn("issue_number", result)
                    self.assertIn("branch_name", result)
                    self.assertIn("feature_name", result)
                    
                    logger.info(f"Feature criada com sucesso: #{result.get('issue_number')}")
                    logger.info(f"Branch: {result.get('branch_name')}")
                    
                except json.JSONDecodeError:
                    self.fail(f"Resposta inválida do MCP: {stdout}")
            
            logger.info("SUCESSO - Teste MCP concluído")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao executar comando: {e}")
            logger.error(f"Saída: {e.stdout}")
            logger.error(f"Erro: {e.stderr}")
            self.fail(f"Erro ao executar make deploy: {e}")
        except Exception as e:
            logger.error(f"FALHA - test_mcp_feature_creation | Erro: {str(e)}", exc_info=True)
            self.fail(f"Teste falhou: {e}")

def run_tests():
    """Função para executar os testes"""
    unittest.main()

if __name__ == '__main__':
    run_tests() 