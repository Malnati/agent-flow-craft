#!/usr/bin/env python3
"""
Módulo de agentes para automação de tarefas.
"""

# Importações essenciais
from .base_agent import BaseAgent
from .local_agent_runner import LocalAgentRunner
from .agent_feature_coordinator import FeatureCoordinatorAgent
from .agent_github_integration import GitHubIntegrationAgent
from .agent_python_refactor import RefactorAgent
from .context_manager import ContextManager

# Lista de módulos exportados
__all__ = [
    'BaseAgent',
    'LocalAgentRunner',
    'FeatureCoordinatorAgent',
    'GitHubIntegrationAgent',
    'RefactorAgent',
    'ContextManager',
]
