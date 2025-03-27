from autogen import AssistantAgent
from autogen.tools import tool
import subprocess
import json
import os
import logging
from slugify import slugify
import re
import time
from pathlib import Path
from agent_platform.core.logger import get_logger, log_execution

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
    def __init__(self, github_token, repo_owner, repo_name):
        logger = get_logger(__name__)
        logger.info(f"INÍCIO - FeatureCreationAgent.__init__ | Parâmetros: repo_owner={repo_owner}, repo_name={repo_name}")
        
        try:
            super().__init__()
            self.github_token = github_token
            self.repo_owner = repo_owner
            self.repo_name = repo_name
            self.logger = logging.getLogger("feature_agent")
            self.check_github_auth()
            logger.debug(f"Agente inicializado para repositório {repo_owner}/{repo_name}")
        except Exception as e:
            logger.error(f"FALHA - FeatureCreationAgent.__init__ | Erro: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info("FIM - FeatureCreationAgent.__init__")

    @log_execution
    def check_github_auth(self):
        logger = get_logger(__name__)
        logger.info("INÍCIO - check_github_auth")
        
        try:
            logger.info("Verificando autenticação do GitHub CLI...")
            subprocess.run(['gh', 'auth', 'status'], check=True, capture_output=True, timeout=15)
            logger.info("Autenticação do GitHub verificada com sucesso.")
        except subprocess.CalledProcessError as e:
            logger.error("Falha na autenticação do GitHub CLI. Execute 'gh auth login' para autenticar.")
            raise
        except Exception as e:
            logger.error(f"FALHA - check_github_auth | Erro: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info("FIM - check_github_auth")

    @log_execution
    def create_github_issue(self, title, body):
        logger = get_logger(__name__)
        logger.info(f"INÍCIO - create_github_issue | Parâmetros: title={title}")
        
        try:
            logger.info(f"Criando issue: {title}")
            # Executar comando gh para criar issue
            result = subprocess.run(
                ['gh', 'issue', 'create', '--title', title, '--body', body],
                check=True, capture_output=True, text=True, timeout=30
            )
            
            issue_url = result.stdout.strip()
            logger.info(f"Saída da criação da issue: {issue_url}")
            
            # Extrair número da issue da URL
            # Formato: https://github.com/owner/repo/issues/123
            issue_number = int(issue_url.split('/')[-1])
            logger.info(f"Issue #{issue_number} criada e capturada com sucesso")
            
            return issue_number
        except Exception as e:
            logger.error(f"FALHA - create_github_issue | Erro: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info("FIM - create_github_issue")

    @log_execution
    def create_branch(self, branch_name):
        logger = get_logger(__name__)
        logger.info(f"INÍCIO - create_branch | Parâmetros: branch_name={branch_name}")
        
        try:
            logger.info(f"Criando branch: {branch_name}")
            subprocess.run(['git', 'checkout', '-b', branch_name], check=True, timeout=30)
            subprocess.run(['git', 'push', '--set-upstream', 'origin', branch_name], check=True, timeout=30)
            logger.info(f"Branch {branch_name} criada e enviada para o repositório remoto")
        except Exception as e:
            logger.error(f"FALHA - create_branch | Erro: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info("FIM - create_branch")

    @log_execution
    def create_pr_plan_file(self, issue_number, prompt_text, execution_plan, branch_name, suggestion=None):
        logger = get_logger(__name__)
        logger.info(f"INÍCIO - create_pr_plan_file | Parâmetros: issue_number={issue_number}, branch_name={branch_name}")
        
        try:
            logger.info(f"Criando arquivo de plano para PR da issue #{issue_number}")
            
            # Preparar conteúdo do arquivo
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            content = (
                f"# Plano de Execução - Issue #{issue_number}\n\n"
                f"Criado em: {timestamp}\n\n"
                f"## Prompt Recebido\n\n{prompt_text}\n\n"
                f"## Plano de Execução\n\n{execution_plan}\n\n"
            )
            
            # Adicionar sugestão se existir
            if suggestion:
                content += f"## Sugestões Adicionais\n\n{suggestion}\n\n"
            
            # Adicionar metadados e links
            content += (
                f"## Metadados\n\n"
                f"- Issue: #{issue_number}\n"
                f"- Branch: `{branch_name}`\n"
            )
            
            # Salvar arquivo
            file_path = f"docs/pr/{issue_number}_feature_plan.md"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Adicionar, commitar e enviar para o repositório
            subprocess.run(['git', 'add', file_path], check=True, timeout=30)
            subprocess.run(['git', 'commit', '-m', f'Add PR plan file for issue #{issue_number}'], check=True, timeout=30)
            subprocess.run(['git', 'push'], check=True, timeout=30)
            
            logger.info("Arquivo de plano de PR criado e enviado para o repositório remoto")
        except Exception as e:
            logger.error(f"FALHA - create_pr_plan_file | Erro: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info("FIM - create_pr_plan_file")

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
        logger = get_logger(__name__)
        logger.info(f"INÍCIO - notify_openai_agent_sdk | Parâmetros: issue_number={issue_number}, branch_name={branch_name}")
        
        try:
            logger.info("Notificando o Agent SDK da OpenAI...")
            
            # Se não houver sugestão, geramos uma
            if not suggestion:
                git_log = self.get_git_main_log()
                ctx = self.get_project_context()
                
                suggestion = self.get_suggestion_from_openai(
                    openai_token, 
                    f"Sugestão para melhoria da issue #{issue_number} no branch {branch_name}",
                    git_log
                )
            
            # Truncar sugestão se for muito longa
            if len(suggestion) > 500:
                logger.debug(f"Sugestão truncada de {len(suggestion)} para 500 caracteres")
                suggestion = suggestion[:497] + "..."
            
            logger.info(f"Notificação enviada para o Agent SDK da OpenAI: {suggestion}")
        except Exception as e:
            logger.error(f"FALHA - notify_openai_agent_sdk | Erro: {str(e)}", exc_info=True)
            # Não vamos propagar esta exceção, pois é apenas uma notificação
            logger.warning("Falha na notificação, mas o processo principal continuará")
        finally:
            logger.info("FIM - notify_openai_agent_sdk")
            
        return suggestion

    @log_execution
    def get_git_main_log(self):
        logger = get_logger(__name__)
        logger.info("INÍCIO - get_git_main_log")
        
        try:
            logger.info("Obtendo histórico de log da branch main")
            result = subprocess.run(
                ['git', 'log', '--oneline', '-n', '10'],
                check=True, capture_output=True, text=True, timeout=15
            )
            return result.stdout
        except Exception as e:
            logger.error(f"FALHA - get_git_main_log | Erro: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info("FIM - get_git_main_log")

    @log_execution
    def get_project_context(self, max_lines=50, max_files=10):
        logger = get_logger(__name__)
        logger.info(f"INÍCIO - get_project_context | Parâmetros: max_lines={max_lines}, max_files={max_files}")
        
        try:
            logger.info("Coletando contexto do projeto")
            context = []
            
            files = _list_project_files_internal(".", 2)
            important_files = [
                f for f in files 
                if f.endswith(('.md', '.py', '.toml', '.json', 'Makefile')) and 
                not f.startswith('venv/') and 
                not '/venv/' in f
            ]
            
            # Limitar a quantidade de arquivos
            important_files = important_files[:max_files]
            
            for file_path in important_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    file_size = len(content)
                    logger.info(f"Arquivo submetido: {file_path} (tamanho: {file_size} bytes)")
                    context.append(f"# File: {file_path}\n\n{content[:max_lines * 80]}")
                except Exception as e:
                    logger.warning(f"Não foi possível ler o arquivo {file_path}: {str(e)}")
            
            return "\n\n".join(context)
        except Exception as e:
            logger.error(f"FALHA - get_project_context | Erro: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info("FIM - get_project_context")

    @log_execution
    def get_suggestion_from_openai(self, openai_token, prompt_text, git_log):
        logger = get_logger(__name__)
        logger.info(f"INÍCIO - get_suggestion_from_openai | Parâmetros: prompt_text={prompt_text[:100]}...")
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=openai_token)
            
            context = f"""
            Repositório: {self.repo_owner}/{self.repo_name}
            
            Histórico de commits recentes:
            {git_log}
            
            Seu papel: Você é um especialista em desenvolvimento de software e deve sugerir melhorias
            para a feature proposta a seguir, considerando as melhores práticas e o contexto do projeto.
            
            Responda em formato JSON com os seguintes campos (apenas JSON, sem textos adicionais):
            - branch_type: tipo de branch (feat, fix, docs, chore, etc)
            - issue_title: título claro e conciso para a issue
            - issue_description: descrição detalhada sobre o que deve ser implementado
            - generated_branch_suffix: sufixo para o nome da branch (usar kebab-case)
            - execution_plan: objeto contendo entregáveis de implementação
            """
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": prompt_text}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=4000
            )
            
            suggestion = response.choices[0].message.content
            logger.info(f"Sugestão recebida do OpenAI: {suggestion[:100]}...")
            logger.debug(f"Sugestão completa: {suggestion}")
            
            return suggestion
        except Exception as e:
            logger.error(f"FALHA - get_suggestion_from_openai | Erro: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info("FIM - get_suggestion_from_openai")

    @log_execution
    def execute_feature_creation(self, prompt_text, execution_plan, openai_token=None):
        logger = get_logger(__name__)
        logger.info(f"INÍCIO - execute_feature_creation | Parâmetros: prompt_text={prompt_text[:100]}...")
        
        try:
            logger.info("Iniciando processo de criação de feature")
            
            git_log = self.get_git_main_log()
            context = self.get_project_context()
            
            # Obter sugestão do OpenAI para criar nomes adequados
            suggestion_json = self.get_suggestion_from_openai(
                openai_token, 
                prompt_text, 
                git_log
            )
            
            suggestion = json.loads(suggestion_json)
            
            # Extrair informações da sugestão
            branch_type = suggestion.get('branch_type', 'feat')
            issue_title = suggestion.get('issue_title', f'Feature: {prompt_text[:50]}...')
            issue_description = suggestion.get('issue_description', execution_plan)
            branch_suffix = suggestion.get('generated_branch_suffix', 'new-feature')
            
            # Criar issue no GitHub
            issue_number = self.create_github_issue(issue_title, issue_description)
            
            # Criar nome da branch baseado na issue
            branch_name = f"{branch_type}/{issue_number}/{branch_suffix}"
            
            # Criar branch
            self.create_branch(branch_name)
            
            # Criar arquivo com plano para PR
            self.create_pr_plan_file(issue_number, prompt_text, execution_plan, branch_name, suggestion_json)
            
            # Criar PR
            self.create_pull_request(branch_name, issue_number)
            
            # Notificar OpenAI (opcional)
            if openai_token:
                self.notify_openai_agent_sdk(openai_token, issue_number, branch_name)
                
            logger.info(f"Processo de criação de feature concluído com sucesso para a issue #{issue_number}")
            
            return issue_number, branch_name
        except Exception as e:
            logger.error(f"FALHA - execute_feature_creation | Erro: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info("FIM - execute_feature_creation")

    @log_execution
    def request_plan_correction(self, prompt, current_plan, validation_result, openai_token):
        logger = get_logger(__name__)
        logger.info(f"INÍCIO - request_plan_correction | Parâmetros: prompt={prompt[:100]}...")
        
        try:
            from openai import OpenAI
            
            # Extrair itens ausentes
            missing_items = validation_result.get("missing_items", [])
            missing_items_text = "\n".join([f"- {item}" for item in missing_items])
            
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
            logger.error(f"FALHA - request_plan_correction | Erro: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info("FIM - request_plan_correction")
