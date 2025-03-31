#!/usr/bin/env python3
"""
MCP Agent - DEPRECATED - MOVED TO new location src/apps/mdc/agent.py

Este arquivo é mantido apenas para compatibilidade. Use a nova localização 
para futuras atualizações.
"""
import os
import sys
import warnings
from pathlib import Path

# Emitir aviso de depreciação
warnings.warn(
    "DEPRECATED: Este arquivo será removido em versões futuras. "
    "Use src/apps/mdc/agent.py em vez disso.",
    DeprecationWarning, 
    stacklevel=2
)

# Adicionar diretório raiz ao path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, root_dir)

# Importar da nova localização
try:
    from src.apps.mdc.agent import main
    
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Erro ao importar da nova localização: {e}")
    print("Por favor, use diretamente src/apps/mdc/agent.py")
    sys.exit(1) 