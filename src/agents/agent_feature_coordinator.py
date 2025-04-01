"""
Agente Coordenador para orquestrar o fluxo de criação de features.
"""
import os

from .agent_feature_concept import FeatureConceptAgent
from .agent_github_integration import GitHubIntegrationAgent
from .agent_concept_generation import ConceptGenerationAgent
from .agent_plan_validator import PlanValidator
from .context_manager import ContextManager
from .agent_tdd_criteria import TDDCriteriaAgent
from .guardrails.out_guardrail_agent_concept_generation import OutGuardrailConceptGenerationAgent
from .guardrails.out_guardrail_agent_tdd_criteria_agent import OutGuardrailTDDCriteriaAgent

from core.logger import get_logger, log_execution

def mask_sensitive_data(data, mask_str='***'):
    """Mascara dados sensíveis para logging."""
    from core.logger import mask_sensitive_data as logger_mask_sensitive_data
    return logger_mask_sensitive_data(data, mask_str)

class FeatureCoordinatorAgent:
    """
    Agente responsável por coordenar todo o fluxo de criação de features.
    
    Este agente orquestra a execução dos diversos agentes especializados,
    garantindo que cada etapa seja executada na ordem correta e com os
    parâmetros adequados.
    """
    
    def __init__(self, openai_token=None, github_token=None, target_dir=None):
        """
        Inicializa o agente coordenador.
        
        Args:
            openai_token: Token da API da OpenAI
            github_token: Token de acesso ao GitHub
            target_dir: Diretório do projeto onde a feature será implementada
        """
        self.logger = get_logger(__name__)
        self.logger.info("INÍCIO - __init__ | Inicializando FeatureCoordinatorAgent")
        
        # Armazenar tokens
        self.openai_token = openai_token or os.environ.get("OPENAI_API_KEY", "")
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN", "")
        
        # Diretório do projeto
        self.target_dir = target_dir or os.getcwd()
        self.logger.debug(f"Diretório do projeto: {self.target_dir}")
        
        # Informações do repositório GitHub
        self.repo_owner = os.environ.get("GITHUB_OWNER", "")
        self.repo_name = os.environ.get("GITHUB_REPO", "")
        
        # Diretório para arquivos de contexto
        self.context_dir = os.environ.get("AGENT_CONTEXT_DIR", "agent_context")
        
        # Instâncias dos agentes (inicializados sob demanda)
        self._concept_agent = None
        self._feature_concept_agent = None
        self._github_agent = None
        self._plan_validator = None
        self._agent_tdd_criteria_agent = None
        self._tdd_guardrail_agent = None
        self._concept_guardrail_agent = None
        
        # Context manager
        self.context_manager = ContextManager(base_dir=self.context_dir)
        
        self.logger.info("SUCESSO - __init__ | FeatureCoordinatorAgent inicializado")
    
    @property
    def concept_agent(self):
        """Obtém ou inicializa o agente de conceito."""
        if self._concept_agent is None:
            self._concept_agent = ConceptGenerationAgent(openai_token=self.openai_token)
        return self._concept_agent
    
    @property
    def feature_concept_agent(self):
        """Obtém ou inicializa o agente de conceito de feature."""
        if self._feature_concept_agent is None:
            self._feature_concept_agent = FeatureConceptAgent(openai_token=self.openai_token)
        return self._feature_concept_agent
    
    @property
    def github_agent(self):
        """Obtém ou inicializa o agente do GitHub."""
        if self._github_agent is None:
            self._github_agent = GitHubIntegrationAgent(
                github_token=self.github_token,
                repo_owner=self.repo_owner,
                repo_name=self.repo_name,
                target_dir=self.target_dir
            )
        return self._github_agent
    
    @property
    def agent_plan_validator(self):
        """Obtém ou inicializa o validador de planos."""
        if self._plan_validator is None:
            self._plan_validator = PlanValidator()
        return self._plan_validator
    
    @property
    def agent_tdd_criteria_agent(self):
        """Obtém ou inicializa o agente de critérios TDD."""
        if self._agent_tdd_criteria_agent is None:
            self._agent_tdd_criteria_agent = TDDCriteriaAgent(openai_token=self.openai_token)
        return self._agent_tdd_criteria_agent
    
    @property
    def tdd_guardrail_agent(self):
        """Obtém ou inicializa o agente de guardrails de TDD."""
        if self._tdd_guardrail_agent is None:
            self._tdd_guardrail_agent = OutGuardrailTDDCriteriaAgent(openai_token=self.openai_token)
        return self._tdd_guardrail_agent
    
    @property
    def concept_guardrail_agent(self):
        """Obtém ou inicializa o agente de guardrails de conceito."""
        if self._concept_guardrail_agent is None:
            self._concept_guardrail_agent = OutGuardrailConceptGenerationAgent(openai_token=self.openai_token)
        return self._concept_guardrail_agent
    
    @log_execution
    async def execute_feature_creation(self, prompt_text, execution_plan=None):
        """
        Executa o fluxo completo de criação de feature.
        
        Args:
            prompt_text: Descrição da feature a ser criada
            execution_plan: Plano de execução opcional
            
        Returns:
            Dict: Resultado da execução com todos os artefatos gerados
        """
        # Inicialização do rastreamento de contexto
        context_chain = {}
        
        self.logger.info(f"INÍCIO - execute_feature_creation | Prompt: '{prompt_text}'")
        
        try:
            # 1. Gerar conceito da feature
            self.logger.info("Etapa 1: Gerando conceito da feature")
            concept_result = self.concept_agent.generate_concept(prompt_text)
            concept_id = concept_result.get("context_id")
            context_chain["concept_id"] = concept_id
            self.logger.info(f"Conceito gerado com ID: {concept_id}")
            
            # 2. Aplicar guardrail no conceito gerado
            self.logger.info("Etapa 2: Aplicando guardrail no conceito")
            guardrail_result = self.concept_guardrail_agent.execute_concept_guardrail(
                concept_id=concept_id,
                prompt=prompt_text,
                project_dir=self.target_dir
            )
            # Usar o conceito melhorado se disponível
            if "improved_concept_id" in guardrail_result:
                concept_id = guardrail_result.get("improved_concept_id")
                context_chain["improved_concept_id"] = concept_id
                self.logger.info(f"Conceito melhorado com ID: {concept_id}")
            
            # 3. Gerar conceito de feature detalhado
            self.logger.info("Etapa 3: Gerando conceito detalhado da feature")
            feature_concept = self.feature_concept_agent.process_concept(concept_id, self.target_dir)
            feature_concept_id = feature_concept.get("context_id")
            context_chain["feature_concept_id"] = feature_concept_id
            self.logger.info(f"Conceito de feature gerado com ID: {feature_concept_id}")
            
            # 4. Gerar critérios TDD
            self.logger.info("Etapa 4: Gerando critérios TDD")
            tdd_criteria = self.agent_tdd_criteria_agent.generate_tdd_criteria(
                context_id=concept_id, 
                project_dir=self.target_dir
            )
            tdd_criteria_id = tdd_criteria.get("context_id")
            context_chain["tdd_criteria_id"] = tdd_criteria_id
            self.logger.info(f"Critérios TDD gerados com ID: {tdd_criteria_id}")
            
            # 5. Aplicar guardrail nos critérios TDD
            self.logger.info("Etapa 5: Aplicando guardrail nos critérios TDD")
            tdd_guardrail_result = self.tdd_guardrail_agent.execute_tdd_guardrail(
                criteria_id=tdd_criteria_id,
                concept_id=concept_id,
                project_dir=self.target_dir
            )
            # Usar os critérios melhorados se disponíveis
            if "improved_criteria_id" in tdd_guardrail_result:
                tdd_criteria_id = tdd_guardrail_result.get("improved_criteria_id")
                context_chain["improved_tdd_criteria_id"] = tdd_criteria_id
                self.logger.info(f"Critérios TDD melhorados com ID: {tdd_criteria_id}")
            
            # 6. Validar plano de implementação
            self.logger.info("Etapa 6: Validando plano de implementação")
            execution_plan = feature_concept.get("execution_plan", {})
            validation_result = self.agent_plan_validator.validate(execution_plan, self.openai_token)
            
            if not validation_result.get("is_valid", False):
                self.logger.warning("Plano inválido. Solicitando correção.")
                corrected_plan = self.request_plan_correction(
                    prompt=prompt_text,
                    current_plan=execution_plan,
                    validation_result=validation_result
                )
                execution_plan = corrected_plan
                self.logger.info("Plano corrigido com sucesso")
            
            # 7. Implementar no GitHub
            self.logger.info("Etapa 7: Implementando no GitHub")
            github_result = self.github_agent.process_concept(feature_concept_id)
            context_chain["github_integration_id"] = github_result.get("context_id")
            self.logger.info(f"Integração GitHub concluída: Issue #{github_result.get('issue_number')}")
            
            # 8. Consolidar resultados
            result = {
                "status": "success",
                "context_chain": context_chain,
                "prompt": prompt_text,
                "github_info": {
                    "issue_number": github_result.get("issue_number"),
                    "branch_name": github_result.get("branch_name"),
                    "pr_number": github_result.get("pr_number")
                },
                "concept": concept_result,
                "feature_concept": feature_concept,
                "tdd_criteria": tdd_criteria,
                "execution_plan": execution_plan
            }
            self.logger.info("SUCESSO - execute_feature_creation | Fluxo completo executado com sucesso")
            return result
            
        except Exception as e:
            self.logger.error(f"FALHA - execute_feature_creation | Erro: {str(e)}", exc_info=True)
            
            # Retornar o estado parcial em caso de falha
            error_result = {
                "status": "error",
                "context_chain": context_chain,
                "prompt": prompt_text,
                "error": str(e)
            }
            
            # Adicionar resultados parciais se disponíveis
            if "concept_id" in context_chain:
                error_result["concept"] = self.concept_agent.get_concept_by_id(context_chain["concept_id"])
                
            if "feature_concept_id" in context_chain:
                error_result["feature_concept"] = self.feature_concept_agent.get_feature_concept_by_id(
                    context_chain["feature_concept_id"]
                )
                
            if "tdd_criteria_id" in context_chain:
                error_result["tdd_criteria"] = self.agent_tdd_criteria_agent.get_criteria_by_id(
                    context_chain["tdd_criteria_id"]
                )
                
            return error_result
    
    @log_execution
    def request_plan_correction(self, prompt, current_plan, validation_result):
        """
        Solicita a correção do plano de execução.
        
        Args:
            prompt: Prompt original da feature
            current_plan: Plano atual com problemas
            validation_result: Resultado da validação com erros
            
        Returns:
            Dict: Plano corrigido
        """
        self.logger.info(f"INÍCIO - request_plan_correction | Erros: {validation_result.get('errors')}")
        
        try:
            corrected_plan = current_plan.copy()
            # Implementar lógica de correção usando o agente mais adequado
            # Por enquanto, apenas retornamos o plano atual
            self.logger.info("SUCESSO - request_plan_correction")
            return corrected_plan
            
        except Exception as e:
            self.logger.error(f"FALHA - request_plan_correction | Erro: {str(e)}", exc_info=True)
            # Em caso de falha, retornar o plano original
            return current_plan
    
    @log_execution
    def get_feature_status(self, context_id):
        """
        Obtém o status atual de uma feature pelo ID do contexto.
        
        Args:
            context_id: ID do contexto da feature
            
        Returns:
            Dict: Status atual da feature
        """
        self.logger.info(f"INÍCIO - get_feature_status | Context ID: {context_id}")
        
        try:
            # Buscar o contexto
            context_data = self.context_manager.get_context(context_id)
            
            if not context_data:
                self.logger.warning(f"Contexto não encontrado: {context_id}")
                return {"status": "not_found", "context_id": context_id}
                
            # Determinar o tipo de contexto e buscar informações relacionadas
            context_type = context_data.get("type", "unknown")
            
            result = {
                "status": "found",
                "context_id": context_id,
                "context_type": context_type,
                "timestamp": context_data.get("timestamp"),
                "data": context_data
            }
            
            # Buscar contextos relacionados na cadeia, se existirem
            if "original_concept_id" in context_data:
                related_id = context_data["original_concept_id"]
                result["related_contexts"] = {"concept_id": related_id}
                
            self.logger.info(f"SUCESSO - get_feature_status | Tipo: {context_type}")
            return result
            
        except Exception as e:
            self.logger.error(f"FALHA - get_feature_status | Erro: {str(e)}", exc_info=True)
            return {"status": "error", "context_id": context_id, "error": str(e)}
    
    @log_execution
    def list_features(self, limit=10):
        """
        Lista as features mais recentes.
        
        Args:
            limit: Número máximo de features a serem listadas
            
        Returns:
            List[Dict]: Lista de features
        """
        self.logger.info(f"INÍCIO - list_features | Limit: {limit}")
        
        try:
            # Listar contextos do tipo feature_concept
            feature_concepts = self.context_manager.list_contexts(
                context_type="feature_concept", 
                limit=limit
            )
            
            # Formatar resultados
            results = []
            for fc in feature_concepts:
                try:
                    # Buscar dados completos do contexto
                    context_data = self.context_manager.get_context(fc["id"])
                    
                    # Extrair informações relevantes
                    results.append({
                        "id": fc["id"],
                        "timestamp": fc["timestamp"],
                        "branch_type": context_data.get("branch_type", "unknown"),
                        "issue_title": context_data.get("issue_title", "Sem título"),
                        "original_concept_id": context_data.get("original_concept_id"),
                        "generated_branch_suffix": context_data.get("generated_branch_suffix")
                    })
                except Exception as e:
                    self.logger.warning(f"Erro ao processar contexto {fc['id']}: {str(e)}")
            
            self.logger.info(f"SUCESSO - list_features | Encontrados: {len(results)}")
            return results
            
        except Exception as e:
            self.logger.error(f"FALHA - list_features | Erro: {str(e)}", exc_info=True)
            return []
    
    def create_feature(self, prompt_text, execution_plan=None):
        """
        Versão síncrona de execute_feature_creation para compatibilidade.
        
        Args:
            prompt_text: Descrição da feature a ser criada
            execution_plan: Plano de execução opcional
            
        Returns:
            Dict: Resultado da execução com todos os artefatos gerados
        """
        import asyncio
        return asyncio.run(self.execute_feature_creation(prompt_text, execution_plan)) 