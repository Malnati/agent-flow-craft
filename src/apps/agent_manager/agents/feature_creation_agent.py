from autogen import AssistantAgent
from autogen.tools import tool
import subprocess
import json
import os
import logging
import time
from pathlib import Path
from core.core.logger import get_logger, log_execution
import yaml
from apps.agent_manager.agents.local_agent_runner import LocalAgentRunner, AgentConfig
import asyncio
from openai import OpenAI
import warnings

# Tente importar funções de mascaramento de dados sensíveis
try:
    from core.core.utils import mask_sensitive_data
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

logging.basicConfig(level=logging.DEBUG)

def _list_project_files_internal(directory=".", max_depth=2):
    logger = logging.getLogger(__name__)
    logger.info(f"INÍCIO - _list_project_files_internal | Parâmetros: directory={directory}, max_depth={max_depth}")
    
    try:
        result = []
        for root, dirs, files in os.walk(directory):
            # Verificar a profundidade
            depth = root.count(os.sep) - directory.count(os.sep)
            if depth <= max_depth:
                for file in files:
                    if not file.startswith('.') and not file.endswith('.pyc'):
                        result.append(os.path.join(root, file))
                        logger.debug(f"Arquivo encontrado: {os.path.join(root, file)}")
        
        logger.debug(f"Total de arquivos encontrados: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"FALHA - _list_project_files_internal | Erro: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info(f"FIM - _list_project_files_internal | Arquivos encontrados: {len(result) if 'result' in locals() else 0}")

@tool
def list_project_files():
    logger = logging.getLogger(__name__)
    logger.info("INÍCIO - list_project_files")
    try:
        return _list_project_files_internal()
    except Exception as e:
        logger.error(f"FALHA - list_project_files | Erro: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("FIM - list_project_files")

def _read_project_file_internal(file_path, max_lines=100):
    logger = logging.getLogger(__name__)
    logger.info(f"INÍCIO - _read_project_file_internal | Parâmetros: file_path={file_path}, max_lines={max_lines}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        truncated = len(lines) > max_lines
        logger.debug(f"Arquivo lido: {file_path}, linhas: {len(lines)}, truncado: {truncated}")
        return ''.join(lines[:max_lines]), truncated
    except Exception as e:
        logger.error(f"FALHA - _read_project_file_internal | Erro: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("FIM - _read_project_file_internal")

@tool
def read_project_file():
    logger = logging.getLogger(__name__)
    logger.info("INÍCIO - read_project_file")
    try:
        return _read_project_file_internal()
    except Exception as e:
        logger.error(f"FALHA - read_project_file | Erro: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("FIM - read_project_file")

class FeatureCreationAgent(AssistantAgent):
    """
    DEPRECATED: Esta classe está marcada para remoção. 
    Use FeatureCoordinatorAgent em conjunto com ConceptGenerationAgent e GitHubIntegrationAgent.
    
    O FeatureCoordinatorAgent separa responsabilidades e usa um sistema de contexto para transferência 
    de dados entre agentes especializados. Isso melhora a manutenibilidade e extensibilidade.
    """
    
    def __init__(self, github_token, repo_owner, repo_name):
        # Exibir aviso de deprecação
        warnings.warn(
            "FeatureCreationAgent está depreciado. Migre para o novo FeatureCoordinatorAgent que " +
            "gerencia agentes especializados como ConceptGenerationAgent e GitHubIntegrationAgent.", 
            DeprecationWarning, 
            stacklevel=2
        )
        
        self.logger = get_logger(__name__)
        self.logger.warning(
            "DEPRECIADO - FeatureCreationAgent.__init__ | " +
            "Esta classe será removida em versões futuras. Use FeatureCoordinatorAgent."
        )
        self.logger.info(f"INÍCIO - FeatureCreationAgent.__init__ | Parâmetros: owner={repo_owner}, repo={repo_name}")
        
        try:
            super().__init__(name="FeatureCreationAgent")
            self.github_token = github_token
            self.repo_owner = repo_owner
            self.repo_name = repo_name
            
            # Verifica a autenticação, mas não falha se não for bem-sucedida
            auth_success = self.check_github_auth()
            if not auth_success:
                self.logger.warning("Inicializando FeatureCreationAgent mesmo sem autenticação GitHub confirmada")
            
            self.logger.info("SUCESSO - FeatureCreationAgent inicializado")
        except Exception as e:
            self.logger.error(f"FALHA - FeatureCreationAgent.__init__ | Erro: {str(e)}", exc_info=True)
            raise

    @log_execution
    def check_github_auth(self):
        """Verifica a autenticação do GitHub CLI"""
        self.logger.info("INÍCIO - check_github_auth | Verificando autenticação GitHub")
        
        try:
            # Aumentando o timeout para 30 segundos e adicionando tratamento para falhas de timeout
            try:
                result = subprocess.run(['gh', 'auth', 'status'], 
                                     check=False, capture_output=True, timeout=30, text=True)
                
                if result.returncode == 0:
                    self.logger.info("SUCESSO - Autenticação GitHub verificada")
                    return True
                else:
                    self.logger.warning(f"AVISO - GitHub CLI não autenticado ou com problemas: {result.stderr}")
                    # Continuar mesmo com erro na autenticação
                    return False
                    
            except subprocess.TimeoutExpired:
                self.logger.warning("AVISO - Timeout ao verificar autenticação GitHub. Continuando mesmo assim.")
                return False
            
        except Exception as e:
            self.logger.error(f"FALHA - check_github_auth | Erro inesperado: {str(e)}", exc_info=True)
            # Permitir continuar mesmo com erro
            return False

    @log_execution
    def create_github_issue(self, title, body):
        """Cria uma nova issue no GitHub"""
        self.logger.info(f"INÍCIO - create_github_issue | Title: {title[:100]}...")
        
        try:
            result = subprocess.run(
                ['gh', 'issue', 'create', '--title', title, '--body', body],
                check=True, capture_output=True, text=True, timeout=30
            )
            
            issue_url = result.stdout.strip()
            issue_number = int(issue_url.split('/')[-1])
            
            self.logger.info(f"SUCESSO - Issue #{issue_number} criada")
            self.logger.debug(f"URL da issue: {issue_url}")
            
            return issue_number
        except Exception as e:
            self.logger.error(f"FALHA - create_github_issue | Erro: {str(e)}", exc_info=True)
            raise

    @log_execution
    def create_branch(self, branch_name):
        """Cria uma nova branch e faz push para o repositório remoto"""
        self.logger.info(f"INÍCIO - create_branch | Branch: {branch_name}")
        
        try:
            subprocess.run(['git', 'checkout', '-b', branch_name], 
                         check=True, timeout=30)
            subprocess.run(['git', 'push', '--set-upstream', 'origin', branch_name], 
                         check=True, timeout=30)
            
            self.logger.info(f"SUCESSO - Branch {branch_name} criada e enviada")
        except Exception as e:
            self.logger.error(f"FALHA - create_branch | Erro: {str(e)}", exc_info=True)
            raise

    @log_execution
    def create_pr_plan_file(self, issue_number, prompt_text, execution_plan, branch_name):
        """Cria arquivo de plano para PR"""
        self.logger.info(f"INÍCIO - create_pr_plan_file | Issue #{issue_number}")
        
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            file_path = f"docs/pr/{issue_number}_feature_plan.md"
            
            content = (
                f"# Plano de Execução - Issue #{issue_number}\n\n"
                f"Criado em: {timestamp}\n\n"
                f"## Prompt Recebido\n\n{prompt_text}\n\n"
                f"## Plano de Execução\n\n{execution_plan}\n\n"
                f"## Metadados\n\n"
                f"- Issue: #{issue_number}\n"
                f"- Branch: `{branch_name}`\n"
            )
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            self.logger.debug(f"Diretório criado: {os.path.dirname(file_path)}")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            subprocess.run(['git', 'add', file_path], check=True, timeout=30)
            subprocess.run(['git', 'commit', '-m', f'Add PR plan file for issue #{issue_number}'], 
                         check=True, timeout=30)
            subprocess.run(['git', 'push'], check=True, timeout=30)
            
            self.logger.info(f"SUCESSO - Arquivo de plano criado e enviado: {file_path}")
        except Exception as e:
            self.logger.error(f"FALHA - create_pr_plan_file | Erro: {str(e)}", exc_info=True)
            raise

    @log_execution
    def create_pull_request(self, branch_name, issue_number):
        logger = get_logger(__name__)
        logger.info(f"INÍCIO - create_pull_request | Parâmetros: branch_name={branch_name}, issue_number={issue_number}")
        
        try:
            logger.info(f"Criando pull request para a issue #{issue_number} da branch {branch_name}")
            
            # Criar PR usando GitHub CLI
            subprocess.run([
                'gh', 'pr', 'create',
                '--base', 'main',
                '--head', branch_name,
                '--title', f'Automated PR for issue #{issue_number}',
                '--body', f'This PR closes issue #{issue_number} and includes the execution plan in `docs/pr/{issue_number}_feature_plan.md`.'
            ], check=True, timeout=30)
            
            logger.info(f"Pull request criado com sucesso para a issue #{issue_number}")
        except Exception as e:
            logger.error(f"FALHA - create_pull_request | Erro: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info("FIM - create_pull_request")

    @log_execution
    def notify_openai_agent_sdk(self, openai_token, issue_number, branch_name, suggestion=None):
        """Notifica o Agent SDK da OpenAI sobre a nova feature"""
        self.logger.info(f"INÍCIO - notify_openai_agent_sdk | Issue #{issue_number}")
        
        try:
            if not suggestion:
                git_log = self.get_git_main_log()
                suggestion = self.get_suggestion_from_openai(
                    openai_token, 
                    f"Sugestão para issue #{issue_number}",
                    git_log
                )
            
            # Truncar sugestão se muito longa
            if len(suggestion) > 500:
                self.logger.debug(f"Sugestão truncada de {len(suggestion)} para 500 caracteres")
                suggestion = suggestion[:497] + "..."
            
            # Mascarar tokens sensíveis nos logs
            mask_sensitive_data(openai_token) if openai_token else "não informado"
            self.logger.info(f"Notificando OpenAI sobre criação de issue #{issue_number} e branch {branch_name}")
            
            # Simulação: na implementação real chamaríamos a API do OpenAI Agent SDK
            time.sleep(0.5)  # Simular tempo de resposta da API
            
            self.logger.info(f"OpenAI notificada com sucesso para issue #{issue_number}")
            return suggestion
            
        except Exception as e:
            # Mascarar possíveis tokens na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            self.logger.error(f"FALHA - notify_openai_agent_sdk | Erro: {error_msg}", exc_info=True)
            return None

    @log_execution
    def get_git_main_log(self):
        logger = get_logger(__name__)
        logger.info("INÍCIO - get_git_main_log")
        
        try:
            logger.info("Obtendo histórico de log da branch main")
            try:
                result = subprocess.run(
                    ['git', 'log', '--oneline', '-n', '10'],
                    check=False, capture_output=True, text=True, timeout=15
                )
                
                if result.returncode == 0:
                    return result.stdout
                else:
                    logger.warning(f"AVISO - Comando git log falhou: {result.stderr}")
                    return "Histórico Git não disponível"
                    
            except subprocess.SubprocessError as e:
                logger.warning(f"AVISO - Erro ao executar git log: {str(e)}")
                return "Histórico Git não disponível"
            
        except Exception as e:
            logger.error(f"FALHA - get_git_main_log | Erro: {str(e)}", exc_info=True)
            return "Histórico Git não disponível"
        finally:
            logger.info("FIM - get_git_main_log")

    @log_execution
    def get_project_context(self, max_lines=50, max_files=10):
        logger = get_logger(__name__)
        logger.info(f"INÍCIO - get_project_context | Parâmetros: max_lines={max_lines}, max_files={max_files}")
        
        try:
            logger.info("Coletando contexto do projeto")
            context = []
            
            try:
                files = _list_project_files_internal(".", 2)
                important_files = [
                    f for f in files 
                    if f.endswith(('.md', '.py', '.toml', '.json', 'Makefile')) and 
                    not f.startswith('venv/') and 
                    not '/venv/' in f
                ]
                
                # Limitar a quantidade de arquivos
                important_files = important_files[:max_files]
            except Exception as e:
                logger.warning(f"AVISO - Erro ao listar arquivos: {str(e)}")
                important_files = []
            
            for file_path in important_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    file_size = len(content)
                    logger.info(f"Arquivo submetido: {file_path} (tamanho: {file_size} bytes)")
                    context.append(f"# File: {file_path}\n\n{content[:max_lines * 80]}")
                except Exception as e:
                    logger.warning(f"Não foi possível ler o arquivo {file_path}: {str(e)}")
            
            if not context:
                context.append("# Contexto do projeto\n\nNão foi possível obter contexto do projeto.")
            
            return "\n\n".join(context)
        except Exception as e:
            logger.error(f"FALHA - get_project_context | Erro: {str(e)}", exc_info=True)
            return "Não foi possível obter contexto do projeto."
        finally:
            logger.info("FIM - get_project_context")

    @log_execution
    def get_suggestion_from_openai(self, openai_token, prompt_text, git_log):
        logger = get_logger(__name__)
        # Mascarar token sensível nos logs
        mask_sensitive_data(openai_token) if openai_token else "não informado"
        logger.info(f"INÍCIO - get_suggestion_from_openai | Parâmetros: prompt_text={prompt_text[:100]}...")
        
        try:
            # Não logar o token diretamente
            if has_utils:
                logger.debug(f"Status do token OpenAI: {'disponível' if openai_token else 'não informado'}")
            
            client = OpenAI(api_key=openai_token)
            
            context = f"""
            Repositório: {self.repo_owner}/{self.repo_name}
            
            Histórico de commits recentes:
            {git_log}
            
            Seu papel: Você é um especialista em desenvolvimento de software e deve sugerir melhorias
            para a feature proposta a seguir, considerando as melhores práticas e o contexto do projeto.
            
            Retorne sua resposta no seguinte formato JSON (sem texto adicional):
            {{
                "branch_type": "tipo de branch (feat, fix, docs, chore, etc)",
                "issue_title": "título claro e conciso para a issue",
                "issue_description": "descrição detalhada sobre o que deve ser implementado",
                "generated_branch_suffix": "sufixo para o nome da branch (usar kebab-case)",
                "execution_plan": "objeto contendo entregáveis de implementação"
            }}
            """
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": prompt_text}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            suggestion = response.choices[0].message.content
            # Mascarar possíveis dados sensíveis na resposta
            safe_suggestion = mask_sensitive_data(suggestion[:100])
            logger.info(f"Sugestão recebida do OpenAI: {safe_suggestion}...")
            
            # Garantir que a resposta é um JSON válido
            try:
                return json.loads(suggestion)
            except json.JSONDecodeError:
                logger.warning(f"Resposta não é um JSON válido. Criando JSON padrão.")
                # Criar um JSON padrão como fallback
                default_json = {
                    "branch_type": "feat",
                    "issue_title": f"Feature: {prompt_text[:50]}..." if len(prompt_text) > 50 else f"Feature: {prompt_text}",
                    "issue_description": suggestion if suggestion else prompt_text,
                    "generated_branch_suffix": "new-feature",
                    "execution_plan": {
                        "steps": [
                            "1. Análise do código",
                            "2. Implementação",
                            "3. Testes",
                            "4. Documentação"
                        ]
                    }
                }
                return default_json
            
        except Exception as e:
            # Mascarar possíveis tokens na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"FALHA - get_suggestion_from_openai | Erro: {error_msg}", exc_info=True)
            raise
        finally:
            logger.info("FIM - get_suggestion_from_openai")

    @log_execution
    def execute_feature_creation(self, prompt_text, execution_plan, openai_token=None):
        logger = get_logger(__name__)
        # Mascarar token nos logs
        mask_sensitive_data(openai_token) if openai_token else "não informado" 
        logger.info(f"INÍCIO - execute_feature_creation | Parâmetros: prompt_text={prompt_text[:100]}...")
        
        try:
            logger.info("Iniciando processo de criação de feature")
            
            git_log = self.get_git_main_log()
            self.get_project_context()
            
            # Verificar se estamos em um repositório Git
            is_git_repo = git_log != "Histórico Git não disponível"
            
            if not is_git_repo:
                logger.warning("AVISO - Não estamos em um repositório Git válido. Algumas funcionalidades serão limitadas.")
                
                # Retornar informações de diagnóstico em vez de tentar executar operações Git
                return {
                    "status": "erro",
                    "mensagem": "Não estamos em um repositório Git válido",
                    "prompt": prompt_text,
                    "plano": execution_plan
                }
            
            # Obter sugestão do OpenAI para criar nomes adequados
            try:
                suggestion_json = self.get_suggestion_from_openai(
                    openai_token, 
                    prompt_text, 
                    git_log
                )
                # Não precisamos usar json.loads aqui pois suggestion_json já é um dict
                suggestion = suggestion_json  # Removido o json.loads()
            except Exception as e:
                logger.error(f"Erro ao obter sugestão da OpenAI: {str(e)}")
                suggestion = {
                    "branch_type": "feat",
                    "issue_title": f'Feature: {prompt_text[:50]}...',
                    "issue_description": execution_plan,
                    "generated_branch_suffix": "new-feature"
                }
            
            # Extrair informações da sugestão
            branch_type = suggestion.get('branch_type', 'feat')
            issue_title = suggestion.get('issue_title', f'Feature: {prompt_text[:50]}...')
            issue_description = suggestion.get('issue_description', execution_plan)
            branch_suffix = suggestion.get('generated_branch_suffix', 'new-feature')
            
            # Criar issue no GitHub
            try:
                issue_number = self.create_github_issue(issue_title, issue_description)
            except Exception as e:
                logger.error(f"Erro ao criar issue no GitHub: {str(e)}")
                issue_number = int(time.time())  # Usar timestamp como fallback
            
            # Criar nome da branch baseado na issue
            branch_name = f"{branch_type}/{issue_number}/{branch_suffix}"
            
            # Criar branch
            try:
                self.create_branch(branch_name)
            except Exception as e:
                logger.error(f"Erro ao criar branch {branch_name}: {str(e)}")
            
            # Criar arquivo com plano para PR
            try:
                self.create_pr_plan_file(issue_number, prompt_text, execution_plan, branch_name)
            except Exception as e:
                logger.error(f"Erro ao criar arquivo de plano para PR: {str(e)}")
            
            # Criar PR
            try:
                self.create_pull_request(branch_name, issue_number)
            except Exception as e:
                logger.error(f"Erro ao criar PR: {str(e)}")
            
            # Notificar OpenAI (opcional)
            if openai_token:
                try:
                    self.notify_openai_agent_sdk(openai_token, issue_number, branch_name)
                except Exception as e:
                    logger.error(f"Erro ao notificar OpenAI: {str(e)}")
            
            logger.info(f"Processo de criação de feature concluído com sucesso para a issue #{issue_number}")
            
            return issue_number, branch_name
        except Exception as e:
            # Mascarar possíveis tokens na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"FALHA - execute_feature_creation | Erro: {error_msg}", exc_info=True)
            
            # Retornar informações de erro em vez de levantar exceção
            return {
                "status": "erro",
                "mensagem": error_msg,
                "prompt": prompt_text,
                "plano": execution_plan
            }
        finally:
            logger.info("FIM - execute_feature_creation")

    @log_execution
    def request_plan_correction(self, prompt, current_plan, validation_result, openai_token):
        logger = get_logger(__name__)
        # Mascarar token nos logs
        mask_sensitive_data(openai_token) if openai_token else "não informado"
        logger.info(f"INÍCIO - request_plan_correction | Parâmetros: prompt={prompt[:100]}...")
        
        try:
            # Extrair itens ausentes
            missing_items = validation_result.get("missing_items", [])
            # Mascarar possíveis dados sensíveis nos itens ausentes
            safe_missing_items = [mask_sensitive_data(item) for item in missing_items]
            missing_items_text = "\n".join([f"- {item}" for item in safe_missing_items])
            
            # Criar mensagem de correção
            correction_message = (
                f"# Solicitação de Correção de Plano\n\n"
                f"## Prompt original:\n{prompt}\n\n"
                f"## Plano atual com problemas:\n{current_plan}\n\n"
                f"## Itens ausentes no plano:\n{missing_items_text}\n\n"
                f"## Instruções:\n"
                f"Por favor, corrija o plano acima incluindo todos os itens ausentes. "
                f"Forneça o plano completo corrigido, não apenas os itens ausentes."
            )
            
            # Mascarar possíveis dados sensíveis na mensagem para log
            safe_msg = mask_sensitive_data(correction_message)
            logger.debug(f"Mensagem de correção preparada: {len(safe_msg)} caracteres")
            
            # Chamar API para correção
            client = OpenAI(api_key=openai_token)
            
            response = client.chat.completions.create(
                model="gpt-4",  # Modelo mais avançado para correção
                messages=[
                    {"role": "system", "content": "Você é um especialista em criar planos de execução de software."},
                    {"role": "user", "content": correction_message}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            corrected_plan = response.choices[0].message.content
            logger.info("Correção do plano recebida")
            return corrected_plan
        except Exception as e:
            # Mascarar possíveis tokens na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"FALHA - request_plan_correction | Erro: {error_msg}", exc_info=True)
            raise
        finally:
            logger.info("FIM - request_plan_correction")

    @log_execution
    async def initialize_local_agents(self):
        """Inicializa agentes locais definidos no YAML"""
        self.logger.info("INÍCIO - initialize_local_agents")
        
        try:
            config_path = Path(".cursor/agents/mcp_local.yaml")
            if not config_path.exists():
                self.logger.warning("Arquivo de configuração de agentes locais não encontrado")
                return
                
            with open(config_path) as f:
                config = yaml.safe_load(f)
                
            self.local_agents = {}
            for agent_config in config.get("local_agents", []):
                agent = LocalAgentRunner(AgentConfig(**agent_config))
                self.local_agents[agent_config["name"]] = agent
                
            self.logger.info(f"SUCESSO - {len(self.local_agents)} agentes locais inicializados")
            
        except Exception as e:
            self.logger.error(f"FALHA - initialize_local_agents | Erro: {str(e)}", exc_info=True)
            raise

async def main():
    """Ponto de entrada para o MCP Server do Cursor"""
    logger = get_logger(__name__)
    logger.info("INÍCIO - MCP Server")
    
    try:
        # Verificar se estamos sendo chamados como MCP Server ou como módulo independente
        if len(sys.argv) > 1 and sys.argv[1] == "--local":
            # Inicialização para uso local
            agent = FeatureCreationAgent(
                github_token=os.environ.get("GITHUB_TOKEN", "seu_token_github"),
                repo_owner=os.environ.get("GITHUB_OWNER", "seu_usuario"),
                repo_name=os.environ.get("GITHUB_REPO", "seu_repositorio")
            )
            
            try:
                # Inicializar agentes MCP
                await agent.initialize_local_agents()
                
                # Usar os agentes
                await criar_nova_feature()
                
            finally:
                # Cleanup
                for local_agent in agent.local_agents.values():
                    await local_agent.stop()
        else:
            # Modo MCP Server
            # Ler configuração do stdin
            import sys
            import json
            
            logger.info("Aguardando comandos do Cursor...")
            
            while True:
                # Ler linha do stdin
                line = sys.stdin.readline().strip()
                if not line:
                    continue
                    
                # Processar comando
                try:
                    command = json.loads(line)
                    message_id = command.get("message_id", "unknown")
                    cmd_type = command.get("command", "unknown")
                    payload = command.get("payload", {})
                    
                    logger.info(f"Comando recebido: {cmd_type} | ID: {message_id}")
                    
                    if cmd_type == "create_feature":
                        # Extrair parâmetros
                        prompt_text = payload.get("prompt", "")
                        github_token = os.environ.get("GITHUB_TOKEN", "")
                        openai_token = os.environ.get("OPENAI_API_KEY", "")
                        
                        # Inicializar agente
                        agent = FeatureCreationAgent(
                            github_token=github_token,
                            repo_owner=os.environ.get("GITHUB_OWNER", ""),
                            repo_name=os.environ.get("GITHUB_REPO", "")
                        )
                        
                        # Criar plano de execução inicial
                        execution_plan = {
                            "steps": [
                                "1. Análise inicial do código",
                                "2. Implementação da feature",
                                "3. Testes unitários",
                                "4. Documentação"
                            ]
                        }
                        
                        # Executar criação da feature
                        issue_number, branch_name = await agent.execute_feature_creation(
                            prompt_text=prompt_text,
                            execution_plan=execution_plan,
                            openai_token=openai_token
                        )
                        
                        # Enviar resposta
                        response = {
                            "message_id": message_id,
                            "status": "success",
                            "result": {
                                "issue_number": issue_number,
                                "branch_name": branch_name
                            }
                        }
                        
                    elif cmd_type == "heartbeat":
                        # Responder heartbeat
                        response = {
                            "message_id": message_id,
                            "status": "alive",
                            "result": {
                                "timestamp": time.time()
                            }
                        }
                        
                    else:
                        # Comando desconhecido
                        response = {
                            "message_id": message_id,
                            "status": "error",
                            "error": f"Comando desconhecido: {cmd_type}"
                        }
                        
                    # Enviar resposta
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
                    
                except Exception as e:
                    # Erro ao processar comando
                    error_response = {
                        "message_id": command.get("message_id", "unknown"),
                        "status": "error",
                        "error": str(e)
                    }
                    sys.stdout.write(json.dumps(error_response) + "\n")
                    sys.stdout.flush()
                    logger.error(f"FALHA - Processamento de comando | Erro: {str(e)}", exc_info=True)
                    
    except Exception as e:
        logger.error(f"FALHA - MCP Server | Erro: {str(e)}", exc_info=True)
    finally:
        logger.info("FIM - MCP Server")

if __name__ == "__main__":
    import sys
    asyncio.run(main())
