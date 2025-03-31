#!/usr/bin/env python3
"""
MCP Agent para integração com o Cursor IDE.

Este módulo implementa um agente MCP que funciona como entry point para
comunicação com a extensão MCP do Cursor IDE, permitindo a execução de comandos
e a criação de features através da interface do Cursor.
"""
import json
import sys
import os
import uuid
import time
import logging
from pathlib import Path
import asyncio

# Tente importar nossas utilidades
try:
    from core.core.utils import mask_sensitive_data
    from core.core.logger import get_logger
    has_utils = True
except ImportError:
    has_utils = False
    # Configuração básica de logging para uso sem dependências
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(str(Path.home() / '.cursor' / 'mcp_agent.log')),
            logging.StreamHandler()
        ]
    )
    
    # Função básica para mascaramento em caso de falha de importação
    def mask_sensitive_data(data, mask_str='***'):
        if isinstance(data, str) and any(s in data.lower() for s in ['token', 'key', 'secret', 'password']):
            # Mostrar parte do início e fim para debugging
            if len(data) > 10:
                return f"{data[:4]}{'*' * 12}{data[-4:] if len(data) > 8 else ''}"
            return mask_str
        return data

# Obter logger ou criar um básico
logger = get_logger('mcp_agent') if has_utils else logging.getLogger('mcp_agent')

class MCPAgent:
    """
    Agente MCP para integração com Cursor IDE.
    Implementa um servidor de comunicação que aceita comandos via stdin/stdout.
    """
    
    def __init__(self):
        """Inicializa o agente MCP."""
        self.commands = {
            "create_feature": self.create_feature,
            "heartbeat": self.heartbeat,
            "run_concept_agent": self.run_concept_agent,
            "run_feature_concept_agent": self.run_feature_concept_agent,
            "run_tdd_criteria_agent": self.run_tdd_criteria_agent,
            "run_github_agent": self.run_github_agent,
            "run_coordinator_agent": self.run_coordinator_agent,
            "run_context_manager": self.run_context_manager,
            "run_validator": self.run_validator,
            "run_refactor_agent": self.run_refactor_agent,
            "run_autoflake_agent": self.run_autoflake_agent
        }
        logger.info("MCPAgent inicializado com comandos: " + ", ".join(self.commands.keys()))

    def create_feature(self, payload):
        """
        Cria uma nova feature baseada no prompt.
        
        Args:
            payload (dict): Payload do comando com prompt e outros parâmetros
            
        Returns:
            dict: Resultado da operação com detalhes da feature
        """
        prompt = payload.get("prompt", "")
        logger.info(f"Criando feature: {prompt[:100]}...")
        
        try:
            # Importar dinamicamente para evitar dependências circulares
            try:
                from apps.agent_manager.agents.feature_coordinator_agent import FeatureCoordinatorAgent
                
                # Obter parâmetros do payload
                github_token = payload.get("github_token", os.environ.get("GITHUB_TOKEN", ""))
                openai_token = payload.get("openai_token", os.environ.get("OPENAI_API_KEY", ""))
                repo_owner = payload.get("owner", os.environ.get("GITHUB_OWNER", ""))
                repo_name = payload.get("repo", os.environ.get("GITHUB_REPO", ""))
                target_dir = payload.get("project_dir", os.getcwd())
                base_branch = payload.get("base_branch", "main")
                context_dir = payload.get("context_dir", "agent_context")
                
                # Inicializar agente
                agent = FeatureCoordinatorAgent(
                    github_token=github_token,
                    openai_token=openai_token,
                    repo_owner=repo_owner,
                    repo_name=repo_name,
                    target_dir=target_dir,
                    base_branch=base_branch
                )
                
                # Configurar o diretório de contexto
                if hasattr(agent, 'context_dir'):
                    agent.context_dir = Path(context_dir)
                
                # Executar criação de feature
                execution_plan = payload.get("execution_plan", None)
                if asyncio.iscoroutinefunction(agent.execute_feature_creation):
                    # Função assíncrona
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    feature_result = loop.run_until_complete(agent.execute_feature_creation(
                        prompt_text=prompt,
                        execution_plan=execution_plan
                    ))
                    loop.close()
                else:
                    # Função síncrona
                    feature_result = agent.create_feature(prompt)
                
                return {
                    "status": "success",
                    "result": feature_result
                }
                
            except ImportError as e:
                logger.error(f"Erro ao importar agente: {str(e)}")
                # Fallback para o comportamento simulado original
                feature_name = prompt.split('\n')[0].strip().lower().replace(' ', '-')[:30]
                issue_number = int(time.time()) % 1000
                branch_name = f"feat/{issue_number}/{feature_name}"
                
                return {
                    "status": "success",
                    "result": {
                        "issue_number": issue_number,
                        "branch_name": branch_name,
                        "feature_name": feature_name,
                        "note": "Usando implementação simulada (agente real não disponível)"
                    }
                }
                
        except Exception as e:
            # Mascarar informações sensíveis na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"Erro ao criar feature: {error_msg}", exc_info=True)
            return {
                "status": "error",
                "error": error_msg
            }
    
    def heartbeat(self, payload):
        """
        Responde a um comando de heartbeat.
        
        Args:
            payload (dict): Payload do comando (não utilizado)
            
        Returns:
            dict: Status da resposta
        """
        return {
            "status": "alive",
            "timestamp": time.time()
        }
    
    def run_concept_agent(self, payload):
        """
        Executa o ConceptGenerationAgent.
        
        Args:
            payload (dict): Parâmetros para o agente
            
        Returns:
            dict: Resultado da operação
        """
        logger.info("Executando ConceptGenerationAgent...")
        
        try:
            # Importar dinamicamente para evitar dependências circulares
            from apps.agent_manager.agents import ConceptGenerationAgent
            
            # Extrair parâmetros
            prompt = payload.get("prompt", "")
            if not prompt:
                return {"status": "error", "error": "Prompt é obrigatório"}
                
            openai_token = payload.get("openai_token", os.environ.get("OPENAI_API_KEY", ""))
            project_dir = payload.get("project_dir", os.getcwd())
            context_dir = payload.get("context_dir", "agent_context")
            model = payload.get("model", "gpt-4-turbo")
            elevation_model = payload.get("elevation_model", "gpt-4-turbo")
            force = payload.get("force", False)
            
            # Criar diretório de contexto se não existir
            Path(context_dir).mkdir(parents=True, exist_ok=True)
            
            # Inicializar agente
            agent = ConceptGenerationAgent(openai_token=openai_token)
            
            # Configurar modelos
            if hasattr(agent, 'set_model'):
                agent.set_model(model)
            if hasattr(agent, 'set_elevation_model'):
                agent.set_elevation_model(elevation_model)
            
            # Configurar força de elevação
            if hasattr(agent, 'set_force_elevation') and force:
                agent.set_force_elevation(True)
                
            # Executar geração de conceito
            result = agent.generate_concept(prompt, project_dir, context_dir)
            
            return {
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"Erro ao executar ConceptGenerationAgent: {error_msg}", exc_info=True)
            return {
                "status": "error",
                "error": error_msg
            }
    
    def run_feature_concept_agent(self, payload):
        """
        Executa o FeatureConceptAgent.
        
        Args:
            payload (dict): Parâmetros para o agente
            
        Returns:
            dict: Resultado da operação
        """
        logger.info("Executando FeatureConceptAgent...")
        
        try:
            # Importar dinamicamente
            from apps.agent_manager.agents import FeatureConceptAgent
            
            # Extrair parâmetros
            concept_id = payload.get("concept_id")
            if not concept_id:
                return {"status": "error", "error": "concept_id é obrigatório"}
                
            openai_token = payload.get("openai_token", os.environ.get("OPENAI_API_KEY", ""))
            project_dir = payload.get("project_dir", os.getcwd())
            context_dir = payload.get("context_dir", "agent_context")
            model = payload.get("model", "gpt-4-turbo")
            elevation_model = payload.get("elevation_model", "gpt-4-turbo")
            force = payload.get("force", False)
            
            # Inicializar agente
            agent = FeatureConceptAgent(openai_token=openai_token)
            
            # Configurar modelos
            if hasattr(agent, 'set_model'):
                agent.set_model(model)
            if hasattr(agent, 'set_elevation_model'):
                agent.set_elevation_model(elevation_model)
            
            # Configurar força de elevação
            if hasattr(agent, 'set_force_elevation') and force:
                agent.set_force_elevation(True)
                
            # Executar processamento de feature concept
            result = agent.process_concept(concept_id, project_dir, context_dir)
            
            return {
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"Erro ao executar FeatureConceptAgent: {error_msg}", exc_info=True)
            return {
                "status": "error",
                "error": error_msg
            }
    
    def run_tdd_criteria_agent(self, payload):
        """
        Executa o TDDCriteriaAgent.
        
        Args:
            payload (dict): Parâmetros para o agente
            
        Returns:
            dict: Resultado da operação
        """
        logger.info("Executando TDDCriteriaAgent...")
        
        try:
            # Importar dinamicamente
            from apps.agent_manager.agents import TDDCriteriaAgent
            
            # Extrair parâmetros
            context_id = payload.get("context_id")
            if not context_id:
                return {"status": "error", "error": "context_id é obrigatório"}
                
            openai_token = payload.get("openai_token", os.environ.get("OPENAI_API_KEY", ""))
            project_dir = payload.get("project_dir", os.getcwd())
            context_dir = payload.get("context_dir", "agent_context")
            model = payload.get("model", "gpt-4-turbo")
            elevation_model = payload.get("elevation_model", "gpt-4-turbo")
            force = payload.get("force", False)
            
            # Inicializar agente
            agent = TDDCriteriaAgent(openai_token=openai_token)
            
            # Configurar modelos
            if hasattr(agent, 'set_model'):
                agent.set_model(model)
            if hasattr(agent, 'set_elevation_model'):
                agent.set_elevation_model(elevation_model)
            
            # Configurar força de elevação
            if hasattr(agent, 'set_force_elevation') and force:
                agent.set_force_elevation(True)
                
            # Executar geração de critérios TDD
            result = agent.generate_tdd_criteria(context_id, project_dir, context_dir)
            
            return {
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"Erro ao executar TDDCriteriaAgent: {error_msg}", exc_info=True)
            return {
                "status": "error",
                "error": error_msg
            }
    
    def run_github_agent(self, payload):
        """
        Executa o GitHubIntegrationAgent.
        
        Args:
            payload (dict): Parâmetros para o agente
            
        Returns:
            dict: Resultado da operação
        """
        logger.info("Executando GitHubIntegrationAgent...")
        
        try:
            # Importar dinamicamente
            from apps.agent_manager.agents import GitHubIntegrationAgent
            
            # Extrair parâmetros
            context_id = payload.get("context_id")
            if not context_id:
                return {"status": "error", "error": "context_id é obrigatório"}
                
            github_token = payload.get("github_token", os.environ.get("GITHUB_TOKEN", ""))
            repo_owner = payload.get("owner", os.environ.get("GITHUB_OWNER", ""))
            repo_name = payload.get("repo", os.environ.get("GITHUB_REPO", ""))
            project_dir = payload.get("project_dir", os.getcwd())
            context_dir = payload.get("context_dir", "agent_context")
            base_branch = payload.get("base_branch", "main")
            
            # Inicializar agente
            agent = GitHubIntegrationAgent(
                github_token=github_token,
                repo_owner=repo_owner,
                repo_name=repo_name
            )
            
            # Executar processamento GitHub
            result = agent.process_feature_concept(context_id, project_dir, context_dir, base_branch)
            
            return {
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"Erro ao executar GitHubIntegrationAgent: {error_msg}", exc_info=True)
            return {
                "status": "error",
                "error": error_msg
            }
    
    def run_coordinator_agent(self, payload):
        """
        Executa o FeatureCoordinatorAgent.
        
        Args:
            payload (dict): Parâmetros para o agente
            
        Returns:
            dict: Resultado da operação
        """
        logger.info("Executando FeatureCoordinatorAgent...")
        
        try:
            # Importar dinamicamente
            from apps.agent_manager.agents import FeatureCoordinatorAgent
            
            # Extrair parâmetros
            prompt = payload.get("prompt")
            if not prompt:
                return {"status": "error", "error": "prompt é obrigatório"}
                
            github_token = payload.get("github_token", os.environ.get("GITHUB_TOKEN", ""))
            openai_token = payload.get("openai_token", os.environ.get("OPENAI_API_KEY", ""))
            repo_owner = payload.get("owner", os.environ.get("GITHUB_OWNER", ""))
            repo_name = payload.get("repo", os.environ.get("GITHUB_REPO", ""))
            project_dir = payload.get("project_dir", os.getcwd())
            context_dir = payload.get("context_dir", "agent_context")
            base_branch = payload.get("base_branch", "main")
            model = payload.get("model", "gpt-4-turbo")
            elevation_model = payload.get("elevation_model", "gpt-4-turbo")
            force = payload.get("force", False)
            plan_file = payload.get("plan_file")
            
            # Carregar plano de execução se fornecido
            execution_plan = None
            if plan_file and os.path.exists(plan_file):
                with open(plan_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    try:
                        execution_plan = json.loads(content)
                    except json.JSONDecodeError:
                        execution_plan = {"steps": [line.strip() for line in content.split('\n') if line.strip()]}
            
            # Inicializar agente
            agent = FeatureCoordinatorAgent(
                github_token=github_token,
                openai_token=openai_token,
                repo_owner=repo_owner,
                repo_name=repo_name,
                target_dir=project_dir,
                base_branch=base_branch
            )
            
            # Configurar o diretório de contexto
            if hasattr(agent, 'context_dir'):
                agent.context_dir = Path(context_dir)
            
            # Configurar modelos nos agentes internos
            if hasattr(agent, 'configure_models'):
                agent.configure_models(model, elevation_model, force)
            
            # Executar criação de feature
            if asyncio.iscoroutinefunction(agent.execute_feature_creation):
                # Executar de forma assíncrona
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(agent.execute_feature_creation(
                    prompt_text=prompt,
                    execution_plan=execution_plan
                ))
                loop.close()
            else:
                # Executar de forma síncrona
                result = agent.create_feature(prompt)
            
            return {
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"Erro ao executar FeatureCoordinatorAgent: {error_msg}", exc_info=True)
            return {
                "status": "error",
                "error": error_msg
            }
    
    def run_context_manager(self, payload):
        """
        Executa o ContextManager.
        
        Args:
            payload (dict): Parâmetros para o gerenciador de contexto
            
        Returns:
            dict: Resultado da operação
        """
        logger.info("Executando ContextManager...")
        
        try:
            # Importar dinamicamente
            from apps.agent_manager.agents import ContextManager
            
            # Extrair parâmetros
            operation = payload.get("operation")
            if not operation:
                return {"status": "error", "error": "operation é obrigatório"}
                
            context_id = payload.get("context_id")
            data_file = payload.get("data_file")
            limit = payload.get("limit", 10)
            context_type = payload.get("type")
            context_dir = payload.get("context_dir", "agent_context")
            days = payload.get("days", 7)
            merge = payload.get("merge", False)
            
            # Criar diretório de contexto se não existir
            Path(context_dir).mkdir(parents=True, exist_ok=True)
            
            # Inicializar gerenciador
            manager = ContextManager(base_dir=context_dir)
            
            # Executar operação solicitada
            result = None
            
            if operation == "listar":
                contexts = manager.list_contexts(context_type=context_type, limit=limit)
                result = contexts
                
            elif operation == "obter":
                if not context_id:
                    return {"status": "error", "error": "context_id é obrigatório para operação 'obter'"}
                context = manager.get_context(context_id)
                result = context
                
            elif operation == "criar":
                if not data_file:
                    return {"status": "error", "error": "data_file é obrigatório para operação 'criar'"}
                    
                # Carregar dados do arquivo
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Criar contexto
                context_id = manager.create_context(data, context_type=context_type)
                result = {"id": context_id}
                
            elif operation == "atualizar":
                if not context_id:
                    return {"status": "error", "error": "context_id é obrigatório para operação 'atualizar'"}
                if not data_file:
                    return {"status": "error", "error": "data_file é obrigatório para operação 'atualizar'"}
                    
                # Carregar dados do arquivo
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Atualizar contexto
                manager.update_context(context_id, data, merge=merge)
                result = {"status": "updated", "id": context_id}
                
            elif operation == "excluir":
                if not context_id:
                    return {"status": "error", "error": "context_id é obrigatório para operação 'excluir'"}
                    
                # Excluir contexto
                manager.delete_context(context_id)
                result = {"status": "deleted", "id": context_id}
                
            elif operation == "limpar":
                # Limpar contextos antigos
                deleted = manager.clean_old_contexts(days=days)
                result = {"status": "cleaned", "deleted_count": len(deleted), "deleted": deleted}
                
            else:
                return {"status": "error", "error": f"Operação desconhecida: {operation}"}
            
            return {
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"Erro ao executar ContextManager: {error_msg}", exc_info=True)
            return {
                "status": "error",
                "error": error_msg
            }
    
    def run_validator(self, payload):
        """
        Executa o PlanValidator.
        
        Args:
            payload (dict): Parâmetros para o validador
            
        Returns:
            dict: Resultado da operação
        """
        logger.info("Executando PlanValidator...")
        
        try:
            # Importar dinamicamente
            from apps.agent_manager.agents import PlanValidator
            
            # Extrair parâmetros
            plan_file = payload.get("plan_file")
            if not plan_file:
                return {"status": "error", "error": "plan_file é obrigatório"}
                
            openai_token = payload.get("openai_token", os.environ.get("OPENAI_API_KEY", ""))
            requirements_file = payload.get("requirements")
            context_dir = payload.get("context_dir", "agent_context")
            project_dir = payload.get("project_dir", os.getcwd())
            model = payload.get("model", "gpt-4-turbo")
            
            # Verificar se o arquivo de plano existe
            if not os.path.exists(plan_file):
                return {"status": "error", "error": f"Arquivo de plano não encontrado: {plan_file}"}
                
            # Carregar plano
            with open(plan_file, 'r', encoding='utf-8') as f:
                content = f.read()
                try:
                    plan = json.loads(content)
                except json.JSONDecodeError:
                    return {"status": "error", "error": "Arquivo de plano não está em formato JSON válido"}
            
            # Inicializar validador
            validator = PlanValidator(openai_token=openai_token)
            
            # Configurar modelo
            if hasattr(validator, 'set_model'):
                validator.set_model(model)
                
            # Executar validação
            validation_result = validator.validate_plan(
                plan=plan,
                requirements_file=requirements_file,
                context_dir=context_dir,
                project_dir=project_dir
            )
            
            return {
                "status": "success",
                "result": validation_result
            }
            
        except Exception as e:
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"Erro ao executar PlanValidator: {error_msg}", exc_info=True)
            return {
                "status": "error",
                "error": error_msg
            }
    
    def run_refactor_agent(self, payload):
        """
        Executa o RefactorAgent.
        
        Args:
            payload (dict): Parâmetros para o agente de refatoração
            
        Returns:
            dict: Resultado da operação
        """
        logger.info("Executando RefactorAgent...")
        
        try:
            # Importar dinamicamente
            from apps.agent_manager.agents.refactor_agent import RefactorAgent
            
            # Extrair parâmetros
            project_dir = payload.get("project_dir")
            if not project_dir:
                return {"status": "error", "error": "project_dir é obrigatório"}
                
            scope = payload.get("scope")
            level = payload.get("level", "moderado")
            dry_run = payload.get("dry_run", False)
            payload.get("output")
            
            # Inicializar agente
            agent = RefactorAgent()
            
            # Executar refatoração
            result = agent.refactor_code(
                project_dir=project_dir,
                scope=scope,
                level=level,
                dry_run=dry_run
            )
            
            return {
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"Erro ao executar RefactorAgent: {error_msg}", exc_info=True)
            return {
                "status": "error",
                "error": error_msg
            }
    
    def run_autoflake_agent(self, payload):
        """
        Executa o AutoflakeAgent.
        
        Args:
            payload (dict): Parâmetros para o agente de limpeza
            
        Returns:
            dict: Resultado da operação
        """
        logger.info("Executando AutoflakeAgent...")
        
        try:
            # Importar dinamicamente
            from apps.agent_manager.agents.autoflake_agent import AutoflakeAgent
            
            # Extrair parâmetros
            project_dir = payload.get("project_dir")
            if not project_dir:
                return {"status": "error", "error": "project_dir é obrigatório"}
                
            scope = payload.get("scope")
            aggressiveness = payload.get("aggressiveness", 2)
            dry_run = payload.get("dry_run", False)
            payload.get("output")
            
            # Inicializar agente
            agent = AutoflakeAgent()
            
            # Executar limpeza
            result = agent.clean_code(
                project_dir=project_dir,
                scope=scope,
                aggressiveness=aggressiveness,
                dry_run=dry_run
            )
            
            return {
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"Erro ao executar AutoflakeAgent: {error_msg}", exc_info=True)
            return {
                "status": "error",
                "error": error_msg
            }
    
    def process_command(self, command):
        """
        Processa um comando recebido.
        
        Args:
            command (dict): Comando a ser processado
            
        Returns:
            dict: Resultado do processamento
        """
        message_id = command.get("message_id", str(uuid.uuid4()))
        cmd_type = command.get("command", "")
        payload = command.get("payload", {})
        
        # Executar o comando se existir
        handler = self.commands.get(cmd_type)
        if handler:
            result = handler(payload)
            result["message_id"] = message_id
            return result
        else:
            return {
                "message_id": message_id,
                "status": "error",
                "error": f"Comando desconhecido: {cmd_type}"
            }
    
    def run(self):
        """
        Executa o loop principal do agente, lendo da entrada padrão
        e enviando respostas para a saída padrão.
        """
        logger.info("MCP Agent iniciado")
        
        try:
            # Processar comandos do stdin
            for line in sys.stdin:
                if not line.strip():
                    continue
                    
                logger.info(f"Comando recebido: {line[:100]}...")
                
                try:
                    # Ler comando JSON
                    command = json.loads(line)
                    result = self.process_command(command)
                    
                    # Enviar resposta
                    print(json.dumps(result), flush=True)
                    logger.info(f"Resposta enviada: {json.dumps(result)[:100]}...")
                    
                except Exception as e:
                    error_response = {
                        "message_id": command.get("message_id", str(uuid.uuid4())) if 'command' in locals() else str(uuid.uuid4()),
                        "status": "error",
                        "error": str(e)
                    }
                    print(json.dumps(error_response), flush=True)
                    logger.error(f"Erro processando comando: {str(e)}", exc_info=True)
        
        except Exception as e:
            logger.error(f"Erro fatal: {str(e)}", exc_info=True)
            sys.exit(1)

def main():
    """Função principal de execução do MCP Agent."""
    agent = MCPAgent()
    agent.run()

if __name__ == "__main__":
    main() 