#!/usr/bin/env python3
"""
MCP Agent para integração com o Cursor IDE.

Este módulo implementa um agente MCP que funciona como entry point para
comunicação com a extensão MCP do Cursor IDE, permitindo a execução de comandos
e a criação de features através da interface do Cursor.
"""
import json
import sys
import os
import uuid
import time
import logging
from pathlib import Path

# Tente importar nossas utilidades
try:
    from core.core.utils import mask_sensitive_data, log_env_status
    from core.core.logger import get_logger
    has_utils = True
except ImportError:
    has_utils = False
    # Configuração básica de logging para uso sem dependências
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(str(Path.home() / '.cursor' / 'mcp_agent.log')),
            logging.StreamHandler()
        ]
    )
    
    # Função básica para mascaramento em caso de falha de importação
    def mask_sensitive_data(data, mask_str='***'):
        if isinstance(data, str) and any(s in data.lower() for s in ['token', 'key', 'secret', 'password']):
            # Mostrar parte do início e fim para debugging
            if len(data) > 10:
                return f"{data[:4]}{'*' * 12}{data[-4:] if len(data) > 8 else ''}"
            return mask_str
        return data

# Obter logger ou criar um básico
logger = get_logger('mcp_agent') if has_utils else logging.getLogger('mcp_agent')

class MCPAgent:
    """
    Agente MCP para integração com Cursor IDE.
    Implementa um servidor de comunicação que aceita comandos via stdin/stdout.
    """
    
    def __init__(self):
        """Inicializa o agente MCP."""
        self.commands = {
            "create_feature": self.create_feature,
            "heartbeat": self.heartbeat
        }
        logger.info("MCPAgent inicializado")

    def create_feature(self, payload):
        """
        Cria uma nova feature baseada no prompt.
        
        Args:
            payload (dict): Payload do comando com prompt e outros parâmetros
            
        Returns:
            dict: Resultado da operação com detalhes da feature
        """
        prompt = payload.get("prompt", "")
        logger.info(f"Criando feature: {prompt[:100]}...")
        
        try:
            # Gerar nome da feature (simplificado)
            feature_name = prompt.split('\n')[0].strip().lower().replace(' ', '-')[:30]
            issue_number = int(time.time()) % 1000
            branch_name = f"feat/{issue_number}/{feature_name}"
            
            # Log dos parâmetros de forma segura
            if has_utils:
                log_env_status(logger, ["GITHUB_TOKEN", "GITHUB_OWNER", "GITHUB_REPO"])
            else:
                logger.info(f"Estado do GITHUB_TOKEN: {'configurado' if os.environ.get('GITHUB_TOKEN') else 'não definido'}")
                logger.info(f"GITHUB_OWNER: {os.environ.get('GITHUB_OWNER', 'não definido')}")
                logger.info(f"GITHUB_REPO: {os.environ.get('GITHUB_REPO', 'não definido')}")
            
            # Criar issue (simulado)
            logger.info(f"Criando issue para: {feature_name}")
            
            # Criar branch (simulado)
            logger.info(f"Criando branch: {branch_name}")
            
            return {
                "status": "success",
                "result": {
                    "issue_number": issue_number,
                    "branch_name": branch_name,
                    "feature_name": feature_name
                }
            }
        except Exception as e:
            # Mascarar informações sensíveis na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"Erro ao criar feature: {error_msg}", exc_info=True)
            return {
                "status": "error",
                "error": error_msg
            }
    
    def heartbeat(self, payload):
        """
        Responde a um comando de heartbeat.
        
        Args:
            payload (dict): Payload do comando (não utilizado)
            
        Returns:
            dict: Status da resposta
        """
        return {
            "status": "alive",
            "timestamp": time.time()
        }
    
    def process_command(self, command):
        """
        Processa um comando recebido.
        
        Args:
            command (dict): Comando a ser processado
            
        Returns:
            dict: Resultado do processamento
        """
        message_id = command.get("message_id", str(uuid.uuid4()))
        cmd_type = command.get("command", "")
        payload = command.get("payload", {})
        
        # Executar o comando se existir
        handler = self.commands.get(cmd_type)
        if handler:
            result = handler(payload)
            result["message_id"] = message_id
            return result
        else:
            return {
                "message_id": message_id,
                "status": "error",
                "error": f"Comando desconhecido: {cmd_type}"
            }
    
    def run(self):
        """
        Executa o loop principal do agente, lendo da entrada padrão
        e enviando respostas para a saída padrão.
        """
        logger.info("MCP Agent iniciado")
        
        try:
            # Processar comandos do stdin
            for line in sys.stdin:
                if not line.strip():
                    continue
                    
                logger.info(f"Comando recebido: {line[:100]}...")
                
                try:
                    # Ler comando JSON
                    command = json.loads(line)
                    result = self.process_command(command)
                    
                    # Enviar resposta
                    print(json.dumps(result), flush=True)
                    logger.info(f"Resposta enviada: {json.dumps(result)[:100]}...")
                    
                except Exception as e:
                    error_response = {
                        "message_id": command.get("message_id", str(uuid.uuid4())) if 'command' in locals() else str(uuid.uuid4()),
                        "status": "error",
                        "error": str(e)
                    }
                    print(json.dumps(error_response), flush=True)
                    logger.error(f"Erro processando comando: {str(e)}", exc_info=True)
        
        except Exception as e:
            logger.error(f"Erro fatal: {str(e)}", exc_info=True)
            sys.exit(1)

def main():
    """Função principal de execução do MCP Agent."""
    agent = MCPAgent()
    agent.run()

if __name__ == "__main__":
    main() 