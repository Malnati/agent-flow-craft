#!/usr/bin/env python3
"""
Script de configuração para testes e2e do MCP
Instala o MCP no Cursor IDE para permitir os testes
"""
import os
import subprocess
import logging
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger('setup_mcp_test')

def main():
    """Função principal de configuração"""
    logger.info("INÍCIO - Configuração do ambiente para testes MCP")
    
    try:
        # Verificar e instalar MCP
        cursor_dir = os.path.expanduser("~/.cursor")
        mcp_agent_path = os.path.join(cursor_dir, "mcp_agent.py")
        mcp_config_path = os.path.join(cursor_dir, "mcp.json")
        
        # Criar diretório do Cursor se não existir
        os.makedirs(cursor_dir, exist_ok=True)
        
        # Verificar se MCP já existe
        if os.path.exists(mcp_agent_path) and os.path.exists(mcp_config_path):
            logger.info("MCP já está instalado, verificando configurações...")
        else:
            logger.info("MCP não encontrado, instalando...")
        
        # Copia o arquivo mcp_agent.py
        script_dir = Path(__file__).resolve().parent
        src_mcp_agent = script_dir / "mcp_agent.py"
        
        if not src_mcp_agent.exists():
            logger.error(f"Arquivo MCP Agent não encontrado em: {src_mcp_agent}")
            sys.exit(1)
        
        # Copiar arquivo com permissões de execução
        subprocess.run(
            ["cp", str(src_mcp_agent), mcp_agent_path],
            check=True
        )
        subprocess.run(
            ["chmod", "+x", mcp_agent_path],
            check=True
        )
        logger.info(f"MCP Agent copiado para: {mcp_agent_path}")
        
        # Criar configuração do MCP
        mcp_config = {
            "mcpServers": {
                "local": {
                    "name": "AgentFlow MCP",
                    "type": "stdio",
                    "config": {
                        "command": mcp_agent_path,
                        "env": {
                            "LOG_LEVEL": "DEBUG",
                            "GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN", ""),
                            "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
                            "GITHUB_OWNER": os.environ.get("GITHUB_OWNER", ""),
                            "GITHUB_REPO": os.environ.get("GITHUB_REPO", "")
                        },
                        "timeout": 30
                    }
                }
            },
            "mcp_default_server": "local",
            "mcp_plugins": {
                "feature_creator": {
                    "name": "Feature Creator",
                    "description": "Cria novas features usando o MCP local",
                    "server": "local",
                    "commands": {
                        "create_feature": {
                            "description": "Cria uma nova feature no projeto",
                            "parameters": {
                                "prompt": {
                                    "type": "string",
                                    "description": "Descrição da feature a ser criada"
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Salvar configuração
        import json
        with open(mcp_config_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        logger.info(f"Configuração MCP salva em: {mcp_config_path}")
        
        # Verificar se existem as variáveis de ambiente necessárias
        required_vars = ['GITHUB_TOKEN', 'GITHUB_OWNER', 'GITHUB_REPO', 'OPENAI_API_KEY']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            logger.warning(f"ATENÇÃO: As seguintes variáveis de ambiente estão faltando: {', '.join(missing_vars)}")
            logger.warning("Os testes podem falhar sem estas variáveis definidas.")
        else:
            logger.info("Todas as variáveis de ambiente necessárias estão configuradas.")
        
        logger.info("SUCESSO - Ambiente de teste MCP configurado com sucesso!")
        return 0
        
    except Exception as e:
        logger.error(f"FALHA - Configuração do ambiente MCP | Erro: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 