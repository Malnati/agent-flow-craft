#!/usr/bin/env python3
"""
Módulo de agentes para o sistema de criação e gestão de features.
"""

from .concept_generation_agent import ConceptGenerationAgent
from .context_manager import ContextManager
from .plan_validator import PlanValidator
from .feature_coordinator_agent import FeatureCoordinatorAgent
from .guardrails.out_guardrail_concept_generation_agent import OutGuardrailConceptGenerationAgent
from .github_integration_agent import GitHubIntegrationAgent
from .linter_agent import LinterAgent
from .testing_agent import TestingAgent
from .tdd_criteria_agent import TDDCriteriaAgent
from .builder_agent import BuilderAgent
from .guardrails.out_guardrail_tdd_criteria_agent import OutGuardrailTDDCriteriaAgent
from .code_documentation_agent import CodeDocumentationAgent

__all__ = [
    'ConceptGenerationAgent',
    'ContextManager',
    'PlanValidator',
    'OutGuardrailConceptGenerationAgent',
    'FeatureCoordinatorAgent',
    'GitHubIntegrationAgent',
    'LinterAgent',
    'TestingAgent',
    'TDDCriteriaAgent',
    'OutGuardrailTDDCriteriaAgent',
    'BuilderAgent',
    'CodeDocumentationAgent',
]
