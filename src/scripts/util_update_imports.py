#!/usr/bin/env python3
"""
Script para mover a funcionalidade de agent_platform para core
e atualizar todas as importações no projeto.
"""
import os
import re
import shutil
from pathlib import Path

def update_imports_in_file(file_path):
    """Atualiza as importações em um arquivo específico."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Substituir importações de agent_platform por core
    modified = re.sub(r'from agent_platform\.', 'from src.core.', content)
    modified = re.sub(r'import agent_platform\.', 'import src.core.', modified)
    
    # Remover referências a src.core e substituir por core
    modified = re.sub(r'from src\.core\.', 'from src.core.', modified)
    modified = re.sub(r'import src\.core\.', 'import src.core.', modified)
    
    # Se o conteúdo foi modificado, escrever de volta ao arquivo
    if modified != content:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified)
        return True
    
    return False

def update_imports_in_directory(directory):
    """Atualiza as importações em todos os arquivos Python em um diretório e subdiretórios."""
    modified_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if update_imports_in_file(file_path):
                    relative_path = os.path.relpath(file_path, directory)
                    modified_files.append(relative_path)
    
    return modified_files

def copy_agent_platform_to_core():
    """Copia os arquivos de agent_platform para core caso não existam."""
    base_dir = Path(__file__).resolve().parent.parent
    agent_platform_dir = base_dir / 'agent_platform'
    core_dir = base_dir / 'core'
    
    # Copia arquivos que não existem
    for root, dirs, files in os.walk(agent_platform_dir):
        # Converter caminho de agent_platform para core
        rel_path = os.path.relpath(root, agent_platform_dir)
        target_dir = os.path.join(core_dir, rel_path)
        
        # Criar diretório se não existir
        os.makedirs(target_dir, exist_ok=True)
        
        # Copiar arquivos que não existem
        for file in files:
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_dir, file)
            
            if not os.path.exists(target_file):
                print(f"Copiando: {source_file} -> {target_file}")
                shutil.copy2(source_file, target_file)

def main():
    """Função principal."""
    base_dir = Path(__file__).resolve().parent.parent
    
    # Copiar arquivos de agent_platform para core
    copy_agent_platform_to_core()
    
    # Atualizar importações
    modified_files = update_imports_in_directory(base_dir)
    
    # Exibir resultados
    print(f"\nAtualizadas importações em {len(modified_files)} arquivos:")
    for file in modified_files:
        print(f"  - {file}")

if __name__ == "__main__":
    main() 