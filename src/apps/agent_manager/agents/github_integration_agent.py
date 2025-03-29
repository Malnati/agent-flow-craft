import subprocess
import json
import os
import time
from pathlib import Path
from agent_platform.core.logger import get_logger, log_execution

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

class GitHubIntegrationAgent:
    """
    Agente responsável pela integração com o GitHub.
    Cria issues, branches e pull requests com base no conceito gerado pelo ConceptGenerationAgent.
    """
    
    def __init__(self, github_token=None, repo_owner=None, repo_name=None, target_dir=None):
        self.logger = get_logger(__name__)
        self.logger.info(f"INÍCIO - GitHubIntegrationAgent.__init__ | Parâmetros: owner={repo_owner}, repo={repo_name}, target_dir={target_dir}")
        
        try:
            self.github_token = github_token or os.environ.get('GITHUB_TOKEN', '')
            self.repo_owner = repo_owner or os.environ.get('GITHUB_OWNER', '')
            self.repo_name = repo_name or os.environ.get('GITHUB_REPO', '')
            self.target_dir = target_dir
            self.context_dir = Path('agent_context')
            
            # Log seguro do status do token
            if has_utils:
                token_status = get_env_status('GITHUB_TOKEN')
                self.logger.debug(f"Status do token GitHub: {token_status}")
            else:
                token_available = "disponível" if self.github_token else "ausente"
                self.logger.debug(f"Status do token GitHub: {token_available}")
            
            if not self.github_token:
                self.logger.warning("ALERTA - Token GitHub ausente | Funcionalidades GitHub serão limitadas")
                
            # Verifica a autenticação, mas não falha se não for bem-sucedida
            auth_success = self.check_github_auth()
            if not auth_success:
                self.logger.warning("Inicializando GithubIntegrationAgent mesmo sem autenticação GitHub confirmada")
            
            self.logger.info("SUCESSO - GitHubIntegrationAgent inicializado")
            
        except Exception as e:
            # Mascarar possíveis tokens na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            self.logger.error(f"FALHA - GitHubIntegrationAgent.__init__ | Erro: {error_msg}", exc_info=True)
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
            if not self.github_token:
                self.logger.warning("Token GitHub ausente. Gerando número de issue simulado.")
                # Gerar número simulado baseado no timestamp
                return int(time.time()) % 10000
                
            # Mudar para o diretório alvo, se especificado
            current_dir = os.getcwd()
            if self.target_dir:
                os.chdir(self.target_dir)
                
            try:
                # Criar issue usando GitHub CLI
                result = subprocess.run(
                    ['gh', 'issue', 'create', '--title', title, '--body', body],
                    check=True, capture_output=True, text=True, timeout=30
                )
                
                issue_url = result.stdout.strip()
                issue_number = int(issue_url.split('/')[-1])
                
                self.logger.info(f"SUCESSO - Issue #{issue_number} criada")
                self.logger.debug(f"URL da issue: {issue_url}")
                
                return issue_number
                
            finally:
                # Voltar ao diretório original
                if self.target_dir:
                    os.chdir(current_dir)
                    
        except Exception as e:
            self.logger.error(f"FALHA - create_github_issue | Erro: {str(e)}", exc_info=True)
            # Gerar número simulado em caso de erro
            return int(time.time()) % 10000
    
    @log_execution
    def create_branch(self, branch_name):
        """Cria uma nova branch e faz push para o repositório remoto"""
        self.logger.info(f"INÍCIO - create_branch | Branch: {branch_name}")
        
        try:
            if not self.github_token:
                self.logger.warning("Token GitHub ausente. Operação de branch simulada.")
                return False
                
            # Mudar para o diretório alvo, se especificado
            current_dir = os.getcwd()
            if self.target_dir:
                os.chdir(self.target_dir)
                
            try:
                # Verificar se estamos em um repositório Git
                try:
                    subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], 
                                check=True, capture_output=True, timeout=15)
                except subprocess.SubprocessError:
                    self.logger.error(f"Não estamos em um repositório Git válido.")
                    return False
                
                # Criar e fazer push da branch
                subprocess.run(['git', 'checkout', '-b', branch_name], 
                            check=True, timeout=30)
                subprocess.run(['git', 'push', '--set-upstream', 'origin', branch_name], 
                            check=True, timeout=30)
                
                self.logger.info(f"SUCESSO - Branch {branch_name} criada e enviada")
                return True
                
            finally:
                # Voltar ao diretório original
                if self.target_dir:
                    os.chdir(current_dir)
                    
        except Exception as e:
            self.logger.error(f"FALHA - create_branch | Erro: {str(e)}", exc_info=True)
            return False
    
    @log_execution
    def create_pr_plan_file(self, issue_number, prompt_text, execution_plan, branch_name):
        """Cria arquivo de plano para PR"""
        self.logger.info(f"INÍCIO - create_pr_plan_file | Issue #{issue_number}")
        
        try:
            if not self.github_token:
                self.logger.warning("Token GitHub ausente. Operação de PR plan simulada.")
                return False
                
            # Mudar para o diretório alvo, se especificado
            current_dir = os.getcwd()
            if self.target_dir:
                os.chdir(self.target_dir)
                
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
                
                # Commit e push das alterações
                subprocess.run(['git', 'add', file_path], check=True, timeout=30)
                subprocess.run(['git', 'commit', '-m', f'Add PR plan file for issue #{issue_number}'], 
                            check=True, timeout=30)
                subprocess.run(['git', 'push'], check=True, timeout=30)
                
                self.logger.info(f"SUCESSO - Arquivo de plano criado e enviado: {file_path}")
                return True
                
            finally:
                # Voltar ao diretório original
                if self.target_dir:
                    os.chdir(current_dir)
                    
        except Exception as e:
            self.logger.error(f"FALHA - create_pr_plan_file | Erro: {str(e)}", exc_info=True)
            return False
    
    @log_execution
    def create_pull_request(self, branch_name, issue_number):
        """Cria um pull request no GitHub"""
        self.logger.info(f"INÍCIO - create_pull_request | Branch: {branch_name}, Issue: #{issue_number}")
        
        try:
            if not self.github_token:
                self.logger.warning("Token GitHub ausente. Operação de PR simulada.")
                return False
                
            # Mudar para o diretório alvo, se especificado
            current_dir = os.getcwd()
            if self.target_dir:
                os.chdir(self.target_dir)
                
            try:
                # Criar PR usando GitHub CLI
                subprocess.run([
                    'gh', 'pr', 'create',
                    '--base', 'main',
                    '--head', branch_name,
                    '--title', f'Automated PR for issue #{issue_number}',
                    '--body', f'This PR closes issue #{issue_number} and includes the execution plan in `docs/pr/{issue_number}_feature_plan.md`.'
                ], check=True, timeout=30)
                
                self.logger.info(f"Pull request criado com sucesso para a issue #{issue_number}")
                return True
                
            finally:
                # Voltar ao diretório original
                if self.target_dir:
                    os.chdir(current_dir)
                    
        except Exception as e:
            self.logger.error(f"FALHA - create_pull_request | Erro: {str(e)}", exc_info=True)
            return False
    
    @log_execution
    def get_git_main_log(self):
        """Obtém o log da branch main"""
        self.logger.info("INÍCIO - get_git_main_log")
        
        try:
            # Mudar para o diretório alvo, se especificado
            current_dir = os.getcwd()
            if self.target_dir:
                os.chdir(self.target_dir)
                
            try:
                result = subprocess.run(
                    ['git', 'log', '--oneline', '-n', '10'],
                    check=False, capture_output=True, text=True, timeout=15
                )
                
                if result.returncode == 0:
                    log = result.stdout
                    self.logger.debug(f"Log Git obtido: {len(log.split(newline))} commits")
                    return log
                else:
                    self.logger.warning(f"AVISO - Comando git log falhou: {result.stderr}")
                    return "Histórico Git não disponível"
                    
            except subprocess.SubprocessError as e:
                self.logger.warning(f"AVISO - Erro ao executar git log: {str(e)}")
                return "Histórico Git não disponível"
                
            finally:
                # Voltar ao diretório original
                if self.target_dir:
                    os.chdir(current_dir)
                    
        except Exception as e:
            self.logger.error(f"FALHA - get_git_main_log | Erro: {str(e)}", exc_info=True)
            return "Histórico Git não disponível"
    
    @log_execution
    def process_concept(self, context_id):
        """
        Processa um conceito previamente gerado pelo ConceptGenerationAgent.
        
        Args:
            context_id (str): ID do contexto a processar
            
        Returns:
            dict: Resultado do processamento com issue_number e branch_name
        """
        self.logger.info(f"INÍCIO - process_concept | Context ID: {context_id}")
        
        try:
            # Carregar o contexto
            context_file = self.context_dir / f"{context_id}.json"
            if not os.path.exists(context_file):
                self.logger.error(f"Arquivo de contexto não encontrado: {context_file}")
                return {"status": "error", "message": "Contexto não encontrado"}
            
            with open(context_file, 'r', encoding='utf-8') as f:
                context_data = json.load(f)
            
            concept = context_data.get("concept", {})
            prompt_text = context_data.get("prompt", "")
            
            # Extrair dados do conceito
            branch_type = concept.get("branch_type", "feat")
            issue_title = concept.get("issue_title", f"Feature: {prompt_text[:50]}...")
            issue_description = concept.get("issue_description", prompt_text)
            branch_suffix = concept.get("generated_branch_suffix", "new-feature")
            execution_plan = json.dumps(concept.get("execution_plan", {}), indent=2)
            
            # Criar issue
            issue_number = self.create_github_issue(issue_title, issue_description)
            
            # Criar nome da branch baseado na issue
            branch_name = f"{branch_type}/{issue_number}/{branch_suffix}"
            
            # Criar branch
            branch_created = self.create_branch(branch_name)
            if not branch_created:
                self.logger.warning(f"Não foi possível criar a branch {branch_name}")
            
            # Criar arquivo com plano para PR
            plan_created = self.create_pr_plan_file(
                issue_number, prompt_text, execution_plan, branch_name
            )
            if not plan_created:
                self.logger.warning(f"Não foi possível criar o arquivo de plano para a issue #{issue_number}")
            
            # Criar PR
            pr_created = self.create_pull_request(branch_name, issue_number)
            if not pr_created:
                self.logger.warning(f"Não foi possível criar o PR para a issue #{issue_number}")
            
            # Salvar o resultado em um novo arquivo de contexto para transferência
            result = {
                "issue_number": issue_number,
                "branch_name": branch_name,
                "branch_created": branch_created,
                "plan_created": plan_created,
                "pr_created": pr_created
            }
            
            # Atualizar o arquivo de contexto
            context_data["github_result"] = result
            context_data["status"] = "completed"
            
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, indent=2)
            
            self.logger.info(f"SUCESSO - Conceito processado | Issue: #{issue_number}, Branch: {branch_name}")
            return result
            
        except Exception as e:
            error_msg = mask_sensitive_data(str(e))
            self.logger.error(f"FALHA - process_concept | Erro: {error_msg}", exc_info=True)
            return {"status": "error", "message": error_msg} 