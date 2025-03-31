#!/usr/bin/env python3
"""
Script de configuração para testes e2e do MCP - DEPRECATED

Este arquivo foi movido para src/apps/mdc/scripts/setup_cursor_env.py
Use a nova localização para futuras atualizações.
"""
import sys
import warnings
from pathlib import Path

# Emitir aviso de depreciação
warnings.warn(
    "DEPRECATED: Este arquivo será removido em versões futuras. "
    "Use src/apps/mdc/scripts/setup_cursor_env.py em vez disso.",
    DeprecationWarning, 
    stacklevel=2
)

# Adicionar diretório raiz ao path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, root_dir)

# Importar da nova localização
try:
    from src.apps.mdc.scripts.setup_cursor_env import main
    
    if __name__ == "__main__":
        sys.exit(main())
except ImportError as e:
    print(f"Erro ao importar da nova localização: {e}")
    print("Por favor, use diretamente src/apps/mdc/scripts/setup_cursor_env.py")
    sys.exit(1) 