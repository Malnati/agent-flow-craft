# Configurações comuns para todos os ambientes
import os
from pathlib import Path

# Constrói caminhos dentro do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Configurações de caminhos
LOG_DIR = os.path.join(BASE_DIR, 'run', 'logs')
CONFIGS_DIR = os.path.join(BASE_DIR, 'configs')