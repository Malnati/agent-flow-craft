from setuptools import setup, find_packages
import subprocess
import os
import time
import re

# Função simples de slugify que não depende de bibliotecas externas
def simple_slugify(text, separator=''):
    # Remover caracteres especiais e converter para minúsculas
    text = re.sub(r'[^\w\s-]', '', text.lower())
    # Substituir espaços e hífens por separador
    text = re.sub(r'[-\s]+', separator, text).strip('-')
    return text

# Obter a versão de forma dinâmica
def get_version():
    # Se existir variável de ambiente VERSION, usar ela como base
    env_version = os.environ.get('VERSION')
    
    if env_version:
        base_version = env_version
    else:
        # Usar ano e mês como MAJOR.MINOR
        year_month = time.strftime('%Y.%m')
        # Usar dia como PATCH
        day = time.strftime('%d')
        base_version = f"{year_month}.{day}"
    
    # Obter o hash curto do último commit
    try:
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        commit_hash = "dev"
    
    # Número de build baseado na hora (para diferenciar builds do mesmo dia)
    build_number = time.strftime('%H%M')
    
    # Formato PEP 440 compatível: X.Y.Z.devABC
    return f"{base_version}.dev{build_number}{simple_slugify(commit_hash, separator='')}"

version = get_version()

setup(
    name="agent_flow_craft",
    version=version,
    packages=find_packages(),
    install_requires=[
        "autogen",
        "pyyaml",
        "python-slugify",
        "openai",
        "asyncio"
    ],
    extras_require={
        'dev': [
            'wheel',
            'pytest',
            'build',
            'twine'
        ]
    },
    entry_points={
        'console_scripts': [
            'mcp_agent=src.core.apps.agent_manager.agents.feature_creation_agent:main',
        ],
    },
    python_requires='>=3.8',
) 