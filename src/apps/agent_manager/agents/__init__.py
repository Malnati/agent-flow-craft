#!/usr/bin/env python3
"""
Módulo de agentes para o sistema de criação e gestão de features.
"""

from .base_agent import BaseAgent
from .local_agent_runner import LocalAgentRunner
from .plan_validator import PlanValidator
from .context_manager import ContextManager
from .concept_generation_agent import ConceptGenerationAgent
from .feature_concept_agent import FeatureConceptAgent
from .github_integration_agent import GitHubIntegrationAgent
from .feature_creation_agent import FeatureCreationAgent
from .feature_coordinator_agent import FeatureCoordinatorAgent
from .guardrails.out_guardrail_concept_generation_agent import OutGuardrailConceptGenerationAgent
from .tdd_criteria_agent import TDDCriteriaAgent
from .guardrails.out_guardrail_tdd_criteria_agent import OutGuardrailTDDCriteriaAgent

# Classes expostas publicamente
__all__ = [
    'BaseAgent',
    'LocalAgentRunner',
    'PlanValidator',
    'ContextManager',
    'ConceptGenerationAgent',
    'FeatureConceptAgent',
    'GitHubIntegrationAgent',
    'FeatureCreationAgent',
    'FeatureCoordinatorAgent',
    'OutGuardrailConceptGenerationAgent',
    'TDDCriteriaAgent',
    'OutGuardrailTDDCriteriaAgent',
]
