from setuptools import setup, find_packages
import subprocess
import os
import time

# Obter a versão de forma dinâmica
def get_version():
    # Se existir variável de ambiente VERSION, usar ela como base
    env_version = os.environ.get('VERSION')
    base_version = env_version if env_version else time.strftime('%Y.%m.%d')
    
    # Obter o hash curto do último commit
    try:
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        commit_hash = "unknown"
    
    # Formato Semantic Versioning 2.0.0: X.Y.Z+COMMIT_HASH
    return f"{base_version}+{commit_hash}"

# Adicionar um número de build único baseado na hora atual para evitar colisões
# apenas se não estiver usando versão manual
version = get_version()
if not os.environ.get('VERSION'):
    build_number = time.strftime('%H%M%S')
    version = f"{version.split('+')[0]}.{build_number}+{version.split('+')[1]}"

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