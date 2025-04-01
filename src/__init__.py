"""
Agent Flow Craft - Framework para automação de fluxo de criação de features.
"""
from src.agents import (
    BaseAgent,
    ConceptGenerationAgent,
    FeatureConceptAgent,
    FeatureCoordinatorAgent,
    GitHubIntegrationAgent,
    PlanValidator,
    TDDCriteriaAgent,
)
from src.core import (
    ModelConfig,
    ModelManager,
    ModelProvider,
    get_env_status,
    get_env_var,
    get_logger,
    log_debug,
    log_error,
    log_info,
    log_warning,
    logger,
    validate_env,
)

__version__ = "2025.04.01.1"

__all__ = [
    # Versão
    "__version__",
    # Agentes
    "BaseAgent",
    "ConceptGenerationAgent",
    "FeatureConceptAgent",
    "FeatureCoordinatorAgent",
    "GitHubIntegrationAgent",
    "PlanValidator",
    "TDDCriteriaAgent",
    # Core
    "ModelManager",
    "ModelProvider",
    "ModelConfig",
    # Ambiente
    "get_env_var",
    "get_env_status",
    "validate_env",
    # Logging
    "logger",
    "get_logger",
    "log_error",
    "log_warning",
    "log_info",
    "log_debug",
]
