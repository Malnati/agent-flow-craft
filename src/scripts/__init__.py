"""
Módulo de scripts e utilitários para execução direta.
"""

# Importações explícitas para facilitar o acesso
from .run_agent_feature_coordinator import main as run_agent_feature_coordinator
from .run_agent_github_integration import main as run_agent_github_integration
from .run_agent_python_refactor import main as run_agent_python_refactor
from .util_generate_docs_index import main as util_generate_docs_index
from .util_clean_pycache import main as util_clean_pycache

# Lista de módulos exportados
__all__ = [
    'run_agent_feature_coordinator',
    'run_agent_github_integration',
    'run_agent_python_refactor',
    'util_generate_docs_index',
    'util_clean_pycache',
] 