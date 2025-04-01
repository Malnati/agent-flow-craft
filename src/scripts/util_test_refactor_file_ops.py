#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar as operações de arquivo com backup do RefactorAgent.
Este script cria uma estrutura de diretórios de teste e demonstra o funcionamento
das operações de movimento e renomeação de arquivos com backup e limpeza.
"""

import os
import sys
import shutil
import tempfile
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("refactor_file_ops_test")

# Adicionar diretório src ao path se executado diretamente
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.agents.agent_python_refactor import RefactorAgent


def setup_test_environment():
    """Configura um ambiente de teste com arquivos e diretórios."""
    # Criar diretório temporário
    test_dir = tempfile.mkdtemp()
    logger.info(f"Diretório de teste criado: {test_dir}")
    
    # Criar estrutura de diretórios
    src_dir = os.path.join(test_dir, "src")
    utils_dir = os.path.join(src_dir, "utils")
    components_dir = os.path.join(src_dir, "components")
    os.path.join(components_dir, "ui")
    
    os.makedirs(utils_dir, exist_ok=True)
    os.makedirs(components_dir, exist_ok=True)
    
    # Criar arquivos de teste
    files = {
        "utils_file": os.path.join(utils_dir, "helpers.py"),
        "component_file": os.path.join(components_dir, "button.py"),
        "empty_dir": os.path.join(utils_dir, "empty")
    }
    
    # Criar conteúdo
    with open(files["utils_file"], "w") as f:
        f.write("# Arquivo de utilitários para teste\n\ndef helper_function():\n    return 'helper'")
    
    with open(files["component_file"], "w") as f:
        f.write("# Componente de botão para teste\n\nclass Button:\n    def render(self):\n        return '<button>'")
    
    # Criar diretório vazio para teste de limpeza
    os.makedirs(files["empty_dir"], exist_ok=True)
    
    return test_dir, files


def test_move_with_backup(test_dir, files):
    """Testa a movimentação de arquivos com backup."""
    # Inicializar agente
    agent = RefactorAgent(
        project_dir=test_dir,
        dry_run=False,
        force=True
    )
    
    # Criar diretório para destino
    ui_dir = os.path.join(os.path.dirname(files["component_file"]), "ui")
    os.makedirs(ui_dir, exist_ok=True)
    
    # Novo caminho para o arquivo de componente
    new_path = os.path.join(ui_dir, "button.py")
    
    # Mover arquivo
    logger.info(f"Movendo arquivo: {files['component_file']} → {new_path}")
    result = agent.move_with_backup(files["component_file"], new_path)
    
    # Verificar resultado
    if result:
        logger.info("✅ Operação de movimentação bem-sucedida")
    else:
        logger.error("❌ Falha na operação de movimentação")
    
    # Verificar backup
    backup_path = os.path.join(test_dir, "bak", os.path.relpath(files["component_file"], test_dir))
    if os.path.exists(backup_path):
        logger.info(f"✅ Backup criado: {backup_path}")
    else:
        logger.error(f"❌ Backup não foi criado: {backup_path}")
    
    return result


def test_rename_file(test_dir, files):
    """Testa a renomeação de arquivos."""
    # Inicializar agente
    agent = RefactorAgent(
        project_dir=test_dir,
        dry_run=False,
        force=True
    )
    
    # Novo nome para o arquivo de utilitários
    utils_dir = os.path.dirname(files["utils_file"])
    new_name = os.path.join(utils_dir, "utility_helpers.py")
    
    # Renomear arquivo
    logger.info(f"Renomeando arquivo: {files['utils_file']} → {new_name}")
    result = agent.rename_file(files["utils_file"], new_name)
    
    # Verificar resultado
    if result:
        logger.info("✅ Operação de renomeação bem-sucedida")
    else:
        logger.error("❌ Falha na operação de renomeação")
    
    # Verificar existência do novo arquivo
    if os.path.exists(new_name):
        logger.info(f"✅ Arquivo renomeado: {new_name}")
    else:
        logger.error(f"❌ Novo arquivo não existe: {new_name}")
    
    # Verificar backup
    backup_path = os.path.join(test_dir, "bak", os.path.relpath(files["utils_file"], test_dir))
    if os.path.exists(backup_path):
        logger.info(f"✅ Backup criado: {backup_path}")
    else:
        logger.error(f"❌ Backup não foi criado: {backup_path}")
    
    # Verificar limpeza de diretório vazio
    empty_dir = files["empty_dir"]
    if not os.path.exists(empty_dir):
        logger.info(f"✅ Diretório vazio removido: {empty_dir}")
    else:
        logger.warning(f"⚠️ Diretório vazio não foi removido: {empty_dir}")
    
    return result


def cleanup(test_dir):
    """Remove diretório de teste."""
    try:
        shutil.rmtree(test_dir)
        logger.info(f"✅ Diretório de teste removido: {test_dir}")
    except Exception as e:
        logger.error(f"❌ Erro ao remover diretório de teste: {str(e)}")


def main():
    """Executa os testes de operações de arquivo."""
    logger.info("Iniciando testes de operações de arquivo com backup")
    
    # Configurar ambiente de teste
    test_dir, files = setup_test_environment()
    
    try:
        # Executar testes
        move_result = test_move_with_backup(test_dir, files)
        rename_result = test_rename_file(test_dir, files)
        
        # Resumo dos resultados
        logger.info("\n--- RESUMO DOS TESTES ---")
        logger.info(f"Movimentação de arquivos: {'✅ PASSOU' if move_result else '❌ FALHOU'}")
        logger.info(f"Renomeação de arquivos: {'✅ PASSOU' if rename_result else '❌ FALHOU'}")
        logger.info(f"Resultado geral: {'✅ PASSOU' if move_result and rename_result else '❌ FALHOU'}")
        
    except Exception as e:
        logger.error(f"Erro durante os testes: {str(e)}", exc_info=True)
    finally:
        # Limpar ambiente
        cleanup(test_dir)
    
    logger.info("Testes concluídos")


if __name__ == "__main__":
    main() 