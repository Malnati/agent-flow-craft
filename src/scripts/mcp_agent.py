#!/usr/bin/env python3
"""
MCP Agent simples para integração com o Cursor IDE
"""
import json
import sys
import os
import uuid
import time
import logging
import subprocess
from pathlib import Path
import argparse

# Tente importar nossas utilidades, com fallback para funcionalidade básica
try:
    from agent_platform.core.utils import mask_sensitive_data, log_env_status, get_env_status
    has_utils = True
except ImportError:
    has_utils = False
    # Função básica para mascaramento em caso de falha de importação
    def mask_sensitive_data(data, mask_str='***'):
        if isinstance(data, str) and any(s in data.lower() for s in ['token', 'key', 'secret', 'password']):
            # Mostrar parte do início e fim para debugging
            if len(data) > 10:
                return f"{data[:4]}{'*' * 12}{data[-4:] if len(data) > 8 else ''}"
            return mask_str
        return data

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.expanduser('~/.cursor/mcp_agent.log'),
    handlers=[
        logging.FileHandler(str(Path.home() / '.cursor' / 'mcp_agent.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('mcp_agent')

def create_feature(prompt):
    """Cria uma nova feature baseada no prompt"""
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

def main():
    """Função principal do MCP Agent"""
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
                message_id = command.get("message_id", str(uuid.uuid4()))
                cmd_type = command.get("command", "")
                payload = command.get("payload", {})
                
                # Processar comando
                if cmd_type == "create_feature":
                    prompt = payload.get("prompt", "")
                    result = create_feature(prompt)
                    result["message_id"] = message_id
                elif cmd_type == "heartbeat":
                    result = {
                        "message_id": message_id,
                        "status": "alive",
                        "timestamp": time.time()
                    }
                else:
                    result = {
                        "message_id": message_id,
                        "status": "error",
                        "error": f"Comando desconhecido: {cmd_type}"
                    }
                
                # Enviar resposta
                print(json.dumps(result), flush=True)
                logger.info(f"Resposta enviada: {json.dumps(result)[:100]}...")
                
            except Exception as e:
                error_response = {
                    "message_id": command.get("message_id", str(uuid.uuid4())),
                    "status": "error",
                    "error": str(e)
                }
                print(json.dumps(error_response), flush=True)
                logger.error(f"Erro processando comando: {str(e)}", exc_info=True)
    
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}", exc_info=True)
        sys.exit(1)
        
if __name__ == "__main__":
    main() 