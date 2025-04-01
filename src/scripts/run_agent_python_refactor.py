#!/usr/bin/env python3
"""
Script para iniciar o agente de refatoração de código.

Este script configura e executa o agente de refatoração, que usa a biblioteca Rope
para identificar e aplicar refatorações automaticamente em um projeto Python.
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

from src.agents.agent_python_refactor import RefactorAgent
from src.core.logger import get_logger

def setup_logger() -> logging.Logger:
    """
    Configura o logger para o script.
    
    Returns:
        logging.Logger: Logger configurado
    """
    logger = get_logger("RefactorAgentScript")
    logger.setLevel(logging.INFO)
    return logger

def parse_arguments() -> argparse.Namespace:
    """
    Analisa os argumentos da linha de comando.
    
    Returns:
        argparse.Namespace: Namespace com os argumentos
    """
    parser = argparse.ArgumentParser(description="Executa o agente de refatoração de código")
    
    parser.add_argument(
        "--project_dir",
        type=str,
        required=True,
        help="Diretório do projeto a ser refatorado"
    )
    
    parser.add_argument(
        "--scope",
        type=str,
        default=None,
        help="Escopo da refatoração (arquivo ou diretório específico, relativo ao project_dir)"
    )
    
    parser.add_argument(
        "--level",
        type=str,
        choices=["leve", "moderado", "agressivo"],
        default="moderado",
        help="Nível de refatoração: leve, moderado (padrão) ou agressivo"
    )
    
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Executa em modo de simulação (não aplica mudanças)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Força a execução da refatoração ignorando restrições de segurança"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="refactor_result.json",
        help="Arquivo de saída para o resultado da refatoração (padrão: refactor_result.json)"
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

def execute_refactor(args: argparse.Namespace, logger: logging.Logger) -> Dict[str, Any]:
    """
    Executa o agente de refatoração com os argumentos fornecidos.
    
    Args:
        args: Argumentos da linha de comando
        logger: Logger para mensagens
        
    Returns:
        Dict[str, Any]: Resultado da refatoração
    """
    try:
        logger.info(f"INÍCIO - Inicializando agente de refatoração | Projeto: {args.project_dir} | Nível: {args.level} | Dry-run: {args.dry_run}")
        
        # Inicializar o agente
        agent_python_refactor = RefactorAgent(
            project_dir=args.project_dir,
            scope=args.scope,
            level=args.level,
            dry_run=args.dry_run,
            force=args.force
        )
        
        # Executar o agente
        result = agent_python_refactor.run()
        
        if result["status"] == "success":
            logger.info(f"SUCESSO - Refatoração concluída | Arquivos analisados: {result['statistics']['files_analyzed']} | Modificados: {result['statistics']['files_modified']}")
        else:
            logger.error(f"FALHA - Erro durante a refatoração: {result.get('message', 'Erro desconhecido')}")
            
        return result
        
    except Exception as e:
        logger.error(f"FALHA - Erro ao executar refatoração: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "statistics": {
                "files_analyzed": 0,
                "files_modified": 0,
                "refactorings_applied": 0,
                "errors": 1,
                "warnings": 0,
                "duration_seconds": 0
            },
            "changes": []
        }

def save_result(result: Dict[str, Any], output_path: str, logger: logging.Logger) -> None:
    """
    Salva o resultado da refatoração em um arquivo JSON.
    
    Args:
        result: Resultado da refatoração
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
    
    # Executar refatoração
    result = execute_refactor(args, logger)
    
    # Salvar resultado
    save_result(result, args.output, logger)
    
    # Definir código de saída com base no status
    sys.exit(0 if result["status"] == "success" else 1)

if __name__ == "__main__":
    main() 