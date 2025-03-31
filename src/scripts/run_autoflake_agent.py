#!/usr/bin/env python3
"""
Script para executar o agente de limpeza de código usando Autoflake.

Este script configura e executa o agente AutoflakeAgent, que remove
imports não utilizados e variáveis não usadas de arquivos Python.
"""
import os
import sys
import json
import argparse
import logging
from typing import Dict, Any

# Adicionar o diretório raiz ao path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, root_dir)

from src.apps.agent_manager.agents.autoflake_agent import AutoflakeAgent
from core.core.logger import get_logger

def setup_logger() -> logging.Logger:
    """
    Configura o logger para o script.
    
    Returns:
        logging.Logger: Logger configurado
    """
    logger = get_logger("AutoflakeAgentScript")
    logger.setLevel(logging.INFO)
    return logger

def parse_arguments() -> argparse.Namespace:
    """
    Analisa os argumentos da linha de comando.
    
    Returns:
        argparse.Namespace: Namespace com os argumentos
    """
    parser = argparse.ArgumentParser(description="Executa o agente de limpeza de código com Autoflake")
    
    parser.add_argument(
        "--project_dir",
        type=str,
        required=True,
        help="Diretório do projeto a ser analisado"
    )
    
    parser.add_argument(
        "--scope",
        type=str,
        default=None,
        help="Escopo da limpeza (arquivo ou diretório específico, relativo ao project_dir)"
    )
    
    parser.add_argument(
        "--aggressiveness",
        type=int,
        choices=[1, 2, 3],
        default=2,
        help="Nível de agressividade: 1 (leve), 2 (moderado - padrão) ou 3 (agressivo)"
    )
    
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Executa em modo de simulação (não aplica mudanças)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Força a execução ignorando restrições de segurança"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="autoflake_result.json",
        help="Arquivo de saída para o resultado da limpeza (padrão: autoflake_result.json)"
    )
    
    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Prompt descritivo da operação (usado apenas para registro)"
    )
    
    return parser.parse_args()

def validate_arguments(args: argparse.Namespace, logger: logging.Logger) -> bool:
    """
    Valida os argumentos fornecidos.
    
    Args:
        args: Argumentos da linha de comando
        logger: Logger para mensagens
        
    Returns:
        bool: True se os argumentos são válidos
    """
    # Validar diretório do projeto
    if not os.path.isdir(args.project_dir):
        logger.error(f"FALHA - Diretório do projeto não encontrado: {args.project_dir}")
        return False
        
    # Validar escopo (se fornecido)
    if args.scope:
        scope_path = os.path.join(args.project_dir, args.scope)
        if not os.path.exists(scope_path):
            logger.error(f"FALHA - Escopo especificado não encontrado: {scope_path}")
            return False
    
    return True

def execute_autoflake(args: argparse.Namespace, logger: logging.Logger) -> Dict[str, Any]:
    """
    Executa o agente de limpeza com os argumentos fornecidos.
    
    Args:
        args: Argumentos da linha de comando
        logger: Logger para mensagens
        
    Returns:
        Dict[str, Any]: Resultado da limpeza
    """
    try:
        logger.info(f"INÍCIO - Inicializando agente de limpeza | Projeto: {args.project_dir} | Agressividade: {args.aggressiveness} | Dry-run: {args.dry_run}")
        
        # Registrar prompt se fornecido
        if args.prompt:
            logger.info(f"Prompt: {args.prompt}")
        
        # Inicializar o agente
        autoflake_agent = AutoflakeAgent(
            project_dir=args.project_dir,
            scope=args.scope,
            aggressiveness=args.aggressiveness,
            dry_run=args.dry_run,
            force=args.force
        )
        
        # Executar o agente
        result = autoflake_agent.run()
        
        if result["status"] == "success":
            logger.info(f"SUCESSO - Limpeza concluída | Arquivos analisados: {result['statistics']['files_analyzed']} | Modificados: {result['statistics']['files_modified']} | Linhas removidas: {result['statistics']['lines_removed']}")
        else:
            logger.error(f"FALHA - Erro durante a limpeza: {result.get('message', 'Erro desconhecido')}")
            
        return result
        
    except Exception as e:
        logger.error(f"FALHA - Erro ao executar limpeza: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "statistics": {
                "files_analyzed": 0,
                "files_modified": 0,
                "lines_removed": 0,
                "errors": 1,
                "warnings": 0,
                "duration_seconds": 0
            },
            "modified_files": []
        }

def save_result(result: Dict[str, Any], output_path: str, logger: logging.Logger) -> None:
    """
    Salva o resultado da limpeza em um arquivo JSON.
    
    Args:
        result: Resultado da limpeza
        output_path: Caminho do arquivo de saída
        logger: Logger para mensagens
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"SUCESSO - Resultado salvo em: {output_path}")
    except Exception as e:
        logger.error(f"FALHA - Erro ao salvar resultado: {str(e)}", exc_info=True)

def main():
    """Função principal do script."""
    # Configurar logger
    logger = setup_logger()
    
    # Analisar argumentos
    args = parse_arguments()
    
    # Validar argumentos
    if not validate_arguments(args, logger):
        sys.exit(1)
    
    # Executar limpeza
    result = execute_autoflake(args, logger)
    
    # Salvar resultado
    save_result(result, args.output, logger)
    
    # Definir código de saída com base no status
    sys.exit(0 if result["status"] == "success" else 1)

if __name__ == "__main__":
    main() 