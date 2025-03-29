import os
import json
import asyncio
from pathlib import Path
from agent_platform.core.logger import get_logger, log_execution

from apps.agent_manager.agents.concept_generation_agent import ConceptGenerationAgent
from apps.agent_manager.agents.github_integration_agent import GitHubIntegrationAgent
from apps.agent_manager.agents.context_manager import ContextManager
from apps.agent_manager.agents.plan_validator import PlanValidator
from apps.agent_manager.agents.tdd_criteria_agent import TDDCriteriaAgent

# Tente importar funções de mascaramento de dados sensíveis
try:
    from agent_platform.core.utils import mask_sensitive_data, get_env_status
    has_utils = True
except ImportError:
    has_utils = False
    # Função básica de fallback para mascaramento
    def mask_sensitive_data(data, mask_str='***'):
        if isinstance(data, str) and any(s in data.lower() for s in ['token', 'key', 'secret', 'password']):
            # Mostrar parte do início e fim para debugging
            if len(data) > 10:
                return f"{data[:4]}{'*' * 12}{data[-4:] if len(data) > 8 else ''}"
            return mask_str
        return data

class FeatureCoordinatorAgent:
    """
    Agente coordenador que orquestra o fluxo entre os diferentes agentes especializados.
    Gerencia a criação de conceitos, validação de planos e integração com GitHub.
    """
    
    def __init__(self, openai_token=None, github_token=None, target_dir=None):
        """
        Inicializa o agente coordenador.
        
        Args:
            openai_token (str, optional): Token de acesso à API da OpenAI.
            github_token (str, optional): Token de acesso à API do GitHub.
            target_dir (str, optional): Diretório alvo do projeto.
        """
        self.logger = get_logger(__name__)
        self.logger.info(f"INÍCIO - {self.__class__.__name__}.__init__")
        
        # Definir atributos
        self.openai_token = openai_token or os.environ.get("OPENAI_API_KEY", "")
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN", "")
        self.target_dir = target_dir or os.getcwd()
        
        # Inicialização lazy dos agentes internos
        self._concept_agent = None
        self._github_agent = None
        self._plan_validator = None
        self._tdd_criteria_agent = None
        
        # Status de tokens (logging seguro)
        openai_token_status = "presente" if self.openai_token else "ausente"
        github_token_status = "presente" if self.github_token else "ausente"
        self.logger.info(f"Token OpenAI: {openai_token_status}")
        self.logger.info(f"Token GitHub: {github_token_status}")
        
        # Informações do diretório alvo
        self.logger.info(f"Diretório alvo: {self.target_dir}")
        
        # Configurar diretório de contexto (padrão ou personalizado)
        self.context_dir = Path("agent_context")
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Diretório de contexto: {self.context_dir.resolve()}")
        
        # Inicializar gerenciador de contexto
        try:
            self.context_manager = ContextManager(base_dir=str(self.context_dir))
            self.logger.info("SUCESSO - FeatureCoordinatorAgent inicializado")
        except Exception as e:
            self.logger.error(f"FALHA - __init__ | Erro ao inicializar: {str(e)}", exc_info=True)
            raise
        
        self.logger.info(f"FIM - {self.__class__.__name__}.__init__")
    
    @property
    def concept_agent(self):
        """Lazy loading do agente de conceito"""
        if self._concept_agent is None:
            self._concept_agent = ConceptGenerationAgent(openai_token=self.openai_token)
        return self._concept_agent
    
    @property
    def github_agent(self):
        """Lazy loading do agente de GitHub"""
        if self._github_agent is None:
            self._github_agent = GitHubIntegrationAgent(
                github_token=self.github_token,
                repo_owner=self.repo_owner,
                repo_name=self.repo_name,
                target_dir=self.target_dir
            )
        return self._github_agent
    
    @property
    def plan_validator(self):
        """Lazy loading do validador de planos"""
        if self._plan_validator is None:
            self._plan_validator = PlanValidator()
        return self._plan_validator
    
    @property
    def tdd_criteria_agent(self):
        """Lazy loading do agente de critérios TDD"""
        if self._tdd_criteria_agent is None:
            self._tdd_criteria_agent = TDDCriteriaAgent(openai_token=self.openai_token)
        return self._tdd_criteria_agent
    
    @log_execution
    async def execute_feature_creation(self, prompt_text, execution_plan=None):
        """
        Coordena o fluxo completo de criação de feature:
        1. Gera conceito via OpenAI
        2. Gera critérios TDD
        3. Valida o plano de execução
        4. Cria issue, branch e PR no GitHub
        
        Args:
            prompt_text (str): Descrição da feature desejada
            execution_plan (dict, optional): Plano de execução pré-definido
            
        Returns:
            dict: Resultado da criação da feature
        """
        self.logger.info(f"INÍCIO - execute_feature_creation | Prompt: {prompt_text[:100]}...")
        
        try:
            # Etapa 1: Obter log do Git para contexto
            git_log = self.github_agent.get_git_main_log()
            
            # Etapa 2: Gerar conceito via ConceptGenerationAgent
            self.logger.info("Gerando conceito via OpenAI")
            concept = self.concept_agent.generate_concept(prompt_text, git_log)
            
            # Salvar conceito no contexto
            concept_data = {
                "prompt": prompt_text,
                "concept": concept,
                "git_log": git_log
            }
            context_id = self.context_manager.create_context(concept_data, "feature_concept")
            
            # Etapa 3: Gerar critérios TDD
            self.logger.info("Gerando critérios TDD")
            tdd_criteria = self.tdd_criteria_agent.generate_tdd_criteria(context_id, self.target_dir)
            self.logger.info(f"Critérios TDD gerados com sucesso: {len(tdd_criteria.get('criteria', []))} critérios")
            
            # Etapa 4: Validar o plano de execução
            if not execution_plan:
                execution_plan = concept.get("execution_plan", {})
                
            execution_plan_str = json.dumps(execution_plan, indent=2)
            self.logger.info("Validando plano de execução")
            
            validation_result = self.plan_validator.validate(
                execution_plan_str, 
                self.openai_token
            )
            
            # Atualizar contexto com a validação
            self.context_manager.update_context(
                context_id, 
                {"validation_result": validation_result}, 
                merge=True
            )
            
            # Se o plano não for válido, solicitar correção
            if not validation_result.get("is_valid", False):
                self.logger.warning("Plano de execução inválido. Solicitando correção.")
                
                # Função auxiliar para correção do plano (será implementada)
                # A implementação atual do FeatureCreationAgent não possui essa função
                
                corrected_plan = self.request_plan_correction(
                    prompt_text,
                    execution_plan_str,
                    validation_result
                )
                
                # Atualizar contexto com o plano corrigido
                self.context_manager.update_context(
                    context_id, 
                    {"corrected_plan": corrected_plan}, 
                    merge=True
                )
                
                # Usar o plano corrigido
                execution_plan = corrected_plan
            
            # Etapa 5: Processar conceito no GitHub
            self.logger.info("Processando conceito no GitHub")
            github_result = self.github_agent.process_concept(context_id)
            
            # Atualizar contexto com o resultado do GitHub
            self.context_manager.update_context(
                context_id, 
                {"github_result": github_result}, 
                merge=True
            )
            
            # Obter o resultado final
            final_context = self.context_manager.get_context(context_id)
            
            result = {
                "context_id": context_id,
                "issue_number": github_result.get("issue_number"),
                "branch_name": github_result.get("branch_name"),
                "plan_valid": validation_result.get("is_valid", False),
                "github_integration_success": github_result.get("status") != "error",
                "tdd_criteria": tdd_criteria,
                "validation_result": validation_result
            }
            
            self.logger.info(f"SUCESSO - Fluxo de criação de feature concluído | Issue: #{result.get('issue_number')}")
            return result
            
        except Exception as e:
            # Mascarar possíveis tokens na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            self.logger.error(f"FALHA - execute_feature_creation | Erro: {error_msg}", exc_info=True)
            
            # Retornar informações de erro
            return {
                "status": "error",
                "message": error_msg,
                "prompt": prompt_text
            }
        finally:
            self.logger.info("FIM - execute_feature_creation")
    
    @log_execution
    def request_plan_correction(self, prompt, current_plan, validation_result):
        """
        Solicita correção do plano de execução.
        
        Args:
            prompt (str): Descrição original da feature
            current_plan (str): Plano atual a ser corrigido
            validation_result (dict): Resultado da validação
            
        Returns:
            dict: Plano corrigido
        """
        self.logger.info("INÍCIO - request_plan_correction")
        
        try:
            # Esta é uma versão simplificada - a implementação completa seria similar
            # à do FeatureCreationAgent.request_plan_correction
            
            # Extrair itens ausentes
            missing_items = validation_result.get("missing_items", [])
            
            # Criar um plano corrigido mínimo
            corrected_plan = {
                "steps": ["Análise", "Implementação", "Testes", "Documentação"],
                "entregaveis": []
            }
            
            # Adicionar um entregável para cada item ausente
            for item in missing_items:
                corrected_plan["entregaveis"].append({
                    "nome": f"Implementação de {item}",
                    "descricao": f"Implementação do requisito: {item}",
                    "dependencias": ["Análise do código"],
                    "exemplo_uso": "// Exemplo de uso será fornecido na implementação",
                    "criterios_aceitacao": ["Testes unitários passando"],
                    "resolucao_problemas": [{"problema": "Possível problema", "resolucao": "Abordagem de resolução"}],
                    "passos_implementacao": ["Análise", "Desenvolvimento", "Testes"]
                })
            
            self.logger.info("SUCESSO - Plano corrigido gerado")
            return corrected_plan
            
        except Exception as e:
            self.logger.error(f"FALHA - request_plan_correction | Erro: {str(e)}", exc_info=True)
            # Retornar um plano mínimo em caso de falha
            return {
                "steps": ["Análise", "Implementação", "Testes", "Documentação"]
            }
        finally:
            self.logger.info("FIM - request_plan_correction")
    
    @log_execution
    def get_feature_status(self, context_id):
        """
        Obtém o status atual de uma feature em criação.
        
        Args:
            context_id (str): ID do contexto da feature
            
        Returns:
            dict: Status atual da feature
        """
        self.logger.info(f"INÍCIO - get_feature_status | Context ID: {context_id}")
        
        try:
            context_data = self.context_manager.get_context(context_id)
            if not context_data:
                self.logger.warning(f"Contexto não encontrado | ID: {context_id}")
                return {"status": "not_found"}
                
            # Extrair status relevantes do contexto
            data = context_data.get("data", {})
            
            status = {
                "context_id": context_id,
                "created_at": context_data.get("created_at"),
                "updated_at": context_data.get("updated_at", context_data.get("created_at")),
                "prompt": data.get("prompt", ""),
                "concept_generated": "concept" in data,
                "plan_validated": "validation_result" in data,
                "plan_valid": data.get("validation_result", {}).get("is_valid", False),
                "github_processed": "github_result" in data,
                "issue_number": data.get("github_result", {}).get("issue_number"),
                "branch_name": data.get("github_result", {}).get("branch_name")
            }
            
            self.logger.info(f"SUCESSO - Status da feature recuperado | ID: {context_id}")
            return status
            
        except Exception as e:
            self.logger.error(f"FALHA - get_feature_status | Erro: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
        finally:
            self.logger.info("FIM - get_feature_status")
    
    @log_execution
    def list_features(self, limit=10):
        """
        Lista as features em processamento.
        
        Args:
            limit (int): Número máximo de features a retornar
            
        Returns:
            list: Lista de features
        """
        self.logger.info(f"INÍCIO - list_features | Limite: {limit}")
        
        try:
            contexts = self.context_manager.list_contexts("feature_concept", limit)
            
            features = []
            for ctx in contexts:
                try:
                    context_data = self.context_manager.get_context(ctx.get("id"))
                    if not context_data:
                        continue
                        
                    data = context_data.get("data", {})
                    features.append({
                        "context_id": ctx.get("id"),
                        "created_at": ctx.get("created_at"),
                        "prompt": data.get("prompt", "")[:100] + "..." if len(data.get("prompt", "")) > 100 else data.get("prompt", ""),
                        "issue_number": data.get("github_result", {}).get("issue_number"),
                        "branch_name": data.get("github_result", {}).get("branch_name")
                    })
                except Exception as e:
                    self.logger.warning(f"Erro ao processar contexto {ctx.get('id')}: {str(e)}")
            
            self.logger.info(f"SUCESSO - Lista de features recuperada | Total: {len(features)}")
            return features
            
        except Exception as e:
            self.logger.error(f"FALHA - list_features | Erro: {str(e)}", exc_info=True)
            return []
        finally:
            self.logger.info("FIM - list_features")

    def create_feature(self, prompt_text, execution_plan=None):
        """
        Método de compatibilidade que chama execute_feature_creation.
        Este método existe para fornecer uma API consistente com outros agentes.
        
        Args:
            prompt_text (str): Descrição da feature desejada
            execution_plan (dict, optional): Plano de execução pré-definido
            
        Returns:
            dict: Resultado da criação da feature
        """
        self.logger.info(f"INÍCIO - create_feature | Prompt: {prompt_text[:100]}...")
        try:
            # Como execute_feature_creation é um método assíncrono,
            # precisamos criar um evento assíncrono e executá-lo em um loop
            import asyncio
            
            # Criar um novo loop de eventos se estiver em um thread diferente
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            # Executar o método assíncrono e obter o resultado
            result = loop.run_until_complete(
                self.execute_feature_creation(prompt_text, execution_plan)
            )
            
            self.logger.info("SUCESSO - create_feature")
            return result
        except Exception as e:
            self.logger.error(f"FALHA - create_feature | Erro: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": str(e),
                "prompt": prompt_text
            }
        finally:
            self.logger.info("FIM - create_feature") 