from setuptools import setup, find_packages
import subprocess
import os
import time
import re
import json

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
    
    # Obter o hash curto do último commit e usar apenas os primeiros 6 dígitos numéricos do timestamp
    # mais os primeiros 4 caracteres do hash convertidos para números (somar os códigos ASCII)
    timestamp = time.strftime('%H%M%S')
    
    # Gerar um número baseado no hash do commit
    commit_hash = None
    try:
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
        # Converter o hash para um número usando a soma dos códigos ASCII dos primeiros 4 caracteres
        hash_num = 0
        for i, c in enumerate(commit_hash[:4]):
            hash_num += ord(c) * (10 ** i)
        hash_num = hash_num % 1000  # Limitar a 3 dígitos
    except (subprocess.SubprocessError, FileNotFoundError):
        hash_num = int(time.time()) % 1000
        commit_hash = "unknown"
    
    # Formato PEP 440 compatível: X.Y.Z.devN (N deve ser um número)
    # Usamos os primeiros dígitos do timestamp + número derivado do hash
    dev_num = int(timestamp[:4] + str(hash_num).zfill(3))
    
    version = f"{base_version}.dev{dev_num}"
    
    # Salvar o mapeamento entre a versão e o commit em um arquivo
    version_map = {}
    map_file = "version_commits.json"
    
    # Carregar mapeamento existente se o arquivo existir
    if os.path.exists(map_file):
        try:
            with open(map_file, 'r') as f:
                version_map = json.load(f)
        except (json.JSONDecodeError, IOError):
            version_map = {}
    
    # Adicionar novo mapeamento
    version_map[version] = {
        "commit_hash": commit_hash,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "build_number": dev_num
    }
    
    # Salvar o mapeamento atualizado
    with open(map_file, 'w') as f:
        json.dump(version_map, f, indent=2)
    
    return version

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
            'mcp_agent=src.core.agents.agent_feature_creation:main',
        ],
    },
    python_requires='>=3.8',
) 