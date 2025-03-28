from setuptools import setup, find_packages
import subprocess
import os
import time
from slugify import slugify

# Obter a versão de forma dinâmica
def get_version():
    # Se existir variável de ambiente VERSION, usar ela como base
    env_version = os.environ.get('VERSION')
    base_version = env_version if env_version else time.strftime('%Y.%m.%d')
    
    # Obter o hash curto do último commit
    try:
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        commit_hash = "dev"
    
    # Formato PEP 440 compatível: X.Y.Z.devN
    # Não podemos usar +COMMIT_HASH no PyPI, então usamos .devCOMMIT_HASH
    return f"{base_version}.dev{slugify(commit_hash, separator='')}"

# Adicionar um número de build único baseado na hora atual para evitar colisões
# apenas se não estiver usando versão manual
version = get_version()
if not os.environ.get('VERSION'):
    build_number = time.strftime('%H%M%S')
    parts = version.split('.dev')
    version = f"{parts[0]}.{build_number}.dev{parts[1] if len(parts) > 1 else ''}"

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