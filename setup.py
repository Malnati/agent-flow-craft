import os
import json
import time
import subprocess
import setuptools
from setuptools import setup

version = os.environ.get('VERSION', '0.0.0.dev0')

# Registra a versão junto com o commit hash no arquivo version_commits.json
if os.environ.get('VERSION') and not version.startswith('0.0.0'):
    try:
        # Tenta obter o hash do commit atual
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        build_number = int(time.strftime('%H%M%S'))
        
        # Carrega o arquivo de mapeamento existente ou cria um novo
        version_map = {}
        if os.path.exists('version_commits.json'):
            with open('version_commits.json', 'r') as f:
                version_map = json.load(f)
        
        # Adiciona a nova versão
        version_map[version] = {
            'commit_hash': commit_hash,
            'timestamp': timestamp,
            'build_number': build_number
        }
        
        # Salva o arquivo atualizado
        with open('version_commits.json', 'w') as f:
            json.dump(version_map, f, indent=2)
            
        print(f"Versão {version} registrada com commit {commit_hash}")
    except Exception as e:
        print(f"Aviso: Não foi possível registrar a versão: {e}")

setup(
    name="agent-flow-craft",
    version=version,
    description="Automatização do fluxo de criação de features via agentes e integração com o GitHub e OpenAI.",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
) 