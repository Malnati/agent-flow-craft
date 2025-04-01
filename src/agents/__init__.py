#!/usr/bin/env python3
"""
Módulo de agentes para o sistema de criação e gestão de features.
"""

from .base_agent import BaseAgent
from .local_agent_runner import LocalAgentRunner
from .agent_plan_validator import PlanValidator
from .context_manager import ContextManager
from .agent_concept_generation import ConceptGenerationAgent
from .agent_feature_concept import FeatureConceptAgent
from .agent_github_integration import GitHubIntegrationAgent
from .agent_feature_creation import FeatureCreationAgent
from .agent_feature_coordinator import FeatureCoordinatorAgent
from .agent_tdd_criteria import TDDCriteriaAgent
from .guardrails.out_guardrail_concept_generation_agent import OutGuardrailConceptGenerationAgent
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
