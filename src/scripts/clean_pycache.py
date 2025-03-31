#!/usr/bin/env python3
"""
Script para limpar diretórios __pycache__ e arquivos .pyc

Este script varre o diretório atual e todos os subdiretórios, removendo:
- Diretórios __pycache__
- Arquivos .pyc, .pyo, .pyd
- Arquivos de cache do pytest
"""

import os
import shutil
import sys
from pathlib import Path

# Tenta importar o logger, mas não falha se não encontrar
try:
    from core.core.logger import get_logger
    logger = get_logger(__name__)
    use_logger = True
except ImportError:
    use_logger = False
    print("Logger não encontrado, usando print para output.")

def log_or_print(message, level="INFO"):
    """Log uma mensagem usando o logger ou print"""
    if use_logger:
        if level == "INFO":
            logger.info(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "ERROR":
            logger.error(message)
        elif level == "DEBUG":
            logger.debug(message)
    else:
        print(f"[{level}] {message}")

def clean_pycache(directory="."):
    """Remove diretórios __pycache__ e arquivos .pyc recursivamente"""
    log_or_print(f"Iniciando limpeza no diretório: {directory}")
    
    # Contadores para estatísticas
    stats = {
        "dirs_removed": 0,
        "files_removed": 0,
        "errors": 0
    }
    
    # Lista de extensões e diretórios para remover
    extensions_to_remove = [".pyc", ".pyo", ".pyd"]
    dirs_to_remove = ["__pycache__", ".pytest_cache"]
    
    # Percorre os diretórios recursivamente
    for root, dirs, files in os.walk(directory, topdown=False):
        # Remove arquivos indesejados
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if any(file.endswith(ext) for ext in extensions_to_remove):
                    os.unlink(file_path)
                    log_or_print(f"Arquivo removido: {file_path}", "DEBUG")
                    stats["files_removed"] += 1
            except Exception as e:
                log_or_print(f"Erro ao remover arquivo {file_path}: {str(e)}", "ERROR")
                stats["errors"] += 1
        
        # Remove diretórios indesejados
        for dir_name in dirs:
            if dir_name in dirs_to_remove:
                dir_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(dir_path)
                    log_or_print(f"Diretório removido: {dir_path}", "DEBUG")
                    stats["dirs_removed"] += 1
                except Exception as e:
                    log_or_print(f"Erro ao remover diretório {dir_path}: {str(e)}", "ERROR")
                    stats["errors"] += 1

    # Exibe estatísticas
    log_or_print(f"Limpeza concluída. Removidos {stats['dirs_removed']} diretórios e {stats['files_removed']} arquivos.")
    if stats["errors"] > 0:
        log_or_print(f"Ocorreram {stats['errors']} erros durante a limpeza.", "WARNING")
    
    return stats

def main():
    """Função principal"""
    if use_logger:
        log_or_print("INÍCIO - clean_pycache")
    
    # Define o diretório para iniciar a limpeza
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = str(Path(__file__).resolve().parent.parent.parent)  # Diretório raiz do projeto
    
    log_or_print(f"Diretório base para limpeza: {directory}")
    stats = clean_pycache(directory)
    
    # Define o código de saída baseado nos erros
    if stats["errors"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    # Define a variável de ambiente para evitar que o próprio script crie arquivos .pyc
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    main() 