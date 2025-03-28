import argparse
import logging
import os
import yaml
from datetime import datetime
import sys
from pathlib import Path
import time
import json
import tempfile
import re

# Função básica de mascaramento (disponível antes de qualquer importação)
def _mask_sensitive_args():
    """Mascara argumentos sensíveis nos parâmetros da linha de comando"""
    # Lista de padrões para argumentos sensíveis
    sensitive_patterns = [
        r'--openai[_-]token',
        r'--token',
        r'--api[_-]key',
        r'--apikey',
        r'--secret',
        r'--password',
        r'sk-[a-zA-Z0-9]{20,}',        # OpenAI API key
        r'sk-proj-[a-zA-Z0-9_-]{20,}',  # OpenAI project API key
        r'gh[pous]_[a-zA-Z0-9]{20,}',  # GitHub tokens
    ]
    
    # Lista de valores a mascarar em argumentos seguintes
    sensitive_arg_prefixes = [
        '--openai-token', '--openai_token', '--token', 
        '--api-key', '--api_key', '--apikey',
        '--secret', '--password'
    ]
    
    # Cópia segura dos argumentos para logging
    safe_args = []
    i = 1  # Começar pelo índice 1 para pular o nome do script
    
    while i < len(sys.argv):
        arg = sys.argv[i]
        safe_arg = arg
        
        # Verificar se o argumento atual é um prefixo sensível e o próximo é o valor
        mask_next_arg = False
        for prefix in sensitive_arg_prefixes:
            if arg == prefix and i+1 < len(sys.argv):
                mask_next_arg = True
                break
        
        # Verificar se o argumento atual contém um valor sensível diretamente
        is_sensitive = False
        if '=' in arg:
            # Para argumentos no formato --arg=valor
            parts = arg.split('=', 1)
            prefix = parts[0]
            value = parts[1]
            
            # Verificar se o prefixo está na lista de argumentos sensíveis
            for s_prefix in sensitive_arg_prefixes:
                if prefix == s_prefix:
                    is_sensitive = True
                    # Preservar parte inicial e final para identificação
                    if len(value) > 8:
                        safe_value = value[:4] + '*'*(len(value)-8) + value[-4:]
                    else:
                        safe_value = '****'
                    safe_arg = f"{prefix}={safe_value}"
                    break
        else:
            # Verificar se é um valor sensível isolado (como um token)
            for pattern in [r'sk-[a-zA-Z0-9]{20,}', r'sk-proj-[a-zA-Z0-9_-]{20,}', r'gh[pous]_[a-zA-Z0-9]{20,}']:
                if re.match(pattern, arg):
                    is_sensitive = True
                    if len(arg) > 8:
                        safe_arg = arg[:4] + '*'*(len(arg)-8) + arg[-4:]
                    else:
                        safe_arg = '****'
                    break
        
        # Adicionar o argumento atual
        safe_args.append(safe_arg)
        
        # Se o próximo argumento precisa ser mascarado
        if mask_next_arg and i+1 < len(sys.argv):
            next_arg = sys.argv[i+1]
            # Mascarar valor sensível
            if len(next_arg) > 8:
                safe_next_arg = next_arg[:4] + '*'*(len(next_arg)-8) + next_arg[-4:]
            else:
                safe_next_arg = '****'
            safe_args.append(safe_next_arg)
            i += 2  # Pular o próximo argumento
        else:
            i += 1  # Avançar normalmente
    
    return ' '.join(safe_args)

# Aplicar mascaramento imediatamente para evitar exposição de tokens
try:
    # Garantir que nenhum token seja exibido quando o script é executado
    if len(sys.argv) > 1:
        safe_command = _mask_sensitive_args()
        print(f"Executando script com argumentos seguros: {safe_command}")
except Exception as e:
    # Em caso de erro no mascaramento, não exibir argumentos
    print(f"Executando {os.path.basename(__file__)} com argumentos mascarados")

from slugify import slugify
from core.core.logger import setup_logging, get_logger, log_execution, mask_sensitive_data

# Adicionar o diretório base ao path para permitir importações
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Project root
SRC_DIR = BASE_DIR / 'src'
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(BASE_DIR))

from src.apps.agent_manager.agents.feature_creation_agent import FeatureCreationAgent
from src.apps.agent_manager.agents.plan_validator import PlanValidator

# Importar utilitários para mascaramento de dados sensíveis
try:
    from agent_platform.core.utils import mask_sensitive_data, log_env_status, get_env_status
    has_utils = True
except ImportError:
    has_utils = False
    # Função básica de fallback para mascaramento
    def mask_sensitive_data(data, mask_str='***'):
        if isinstance(data, str) and any(s in data.lower() for s in ['token', 'key', 'secret', 'password']):
            return mask_str
        return data

def mask_args_for_logging(args):
    """
    Mascara dados sensíveis nos argumentos para logging seguro.
    
    Args:
        args: ArgumentParser namespace com argumentos
        
    Returns:
        dict: Argumentos mascarados para log seguro
    """
    # Converter Namespace para dicionário
    args_dict = vars(args).copy()
    
    # Lista de argumentos sensíveis a mascarar
    sensitive_args = ['token', 'openai_token']
    
    # Mascarar argumentos sensíveis
    for arg_name in sensitive_args:
        if arg_name in args_dict and args_dict[arg_name]:
            # Preservar alguns caracteres para reconhecimento
            value = args_dict[arg_name]
            if len(value) > 10:
                prefix = value[:4]
                suffix = value[-4:] if len(value) > 8 else ""
                args_dict[arg_name] = f"{prefix}{'*' * 12}{suffix}"
            else:
                args_dict[arg_name] = '***'
    
    return args_dict

@log_execution
def setup_logging_for_feature_agent():
    """Configuração específica de logs para o agente de feature"""
    logger = get_logger(__name__)
    logger.info("INÍCIO - setup_logging_for_feature_agent")
    
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file = f"feature_agent_{timestamp}.log"
        logger = setup_logging("feature_agent", log_file)
        logger.info("SUCESSO - Logger configurado")
        return logger
    except Exception as e:
        logger.error(f"FALHA - setup_logging_for_feature_agent | Erro: {str(e)}", exc_info=True)
        raise

# Configurar logging
logger = setup_logging_for_feature_agent()

@log_execution
def ensure_config_files():
    """Garante que todos os arquivos de configuração necessários existam"""
    # Lista de diretórios a serem verificados/criados
    directories = [
        "configs",
        "configs/agents",
        "logs"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Diretório criado: {directory}")
            except Exception as e:
                logger.warning(f"Não foi possível criar o diretório {directory}: {e}")
    
    # Verificar se o arquivo de requisitos existe
    requirements_file = "configs/agents/plan_requirements.yaml"
    if not os.path.exists(requirements_file):
        logger.warning(f"Arquivo de requisitos não encontrado: {requirements_file}")
        # Não é necessário criar o arquivo, pois o validador usará requisitos padrão
        
    # Verificar configuração do logging
    log_config_file = "configs/logging.yaml"
    try:
        if not os.path.exists(log_config_file):
            logger.warning(f"Arquivo de configuração de logging não encontrado: {log_config_file}")
    except Exception as e:
        logger.warning(f"Erro ao verificar arquivo de configuração de logging: {e}")
    
    # Verificar arquivo de ambiente
    env_file = ".env"
    try:
        if not os.path.exists(env_file):
            logger.warning(f"Arquivo de ambiente não encontrado: {env_file}")
    except Exception as e:
        logger.warning(f"Erro ao verificar arquivo de ambiente: {e}")

    logger.info("Verificação de arquivos de configuração concluída")

@log_execution
def main():
    """Função principal do script"""
    logger = get_logger(__name__)
    logger.info("INÍCIO - main")
    
    try:
        ensure_config_files()
        
        parser = argparse.ArgumentParser(description="Execute the feature creation process.")
        parser.add_argument("prompt", type=str, help="The user prompt for feature creation.")
        parser.add_argument("execution_plan", type=str, help="The execution plan for the feature.")
        parser.add_argument("--target", required=True, type=str, 
                          help="Caminho completo para o repositório Git do projeto")
        parser.add_argument("--token", type=str, help="GitHub token", default=os.environ.get("GITHUB_TOKEN"))
        parser.add_argument("--owner", type=str, help="Repository owner (obrigatório).")
        parser.add_argument("--repo", type=str, help="Repository name (obrigatório).")
        parser.add_argument("--openai_token", type=str, help="Token da OpenAI", 
                            default=os.environ.get("OPENAI_API_KEY"))
        parser.add_argument("--max_attempts", type=int, help="Número máximo de tentativas", default=3)
        parser.add_argument("--config", type=str, help="Arquivo de configuração", 
                            default="config/plan_requirements.yaml")
        parser.add_argument("--verbose", action="store_true", help="Ativa modo verbose")
        
        args = parser.parse_args()
        
        # Log seguro dos argumentos (mascarando dados sensíveis)
        safe_args = mask_args_for_logging(args)
        logger.debug(f"Argumentos: {safe_args}")
        
        if args.verbose:
            logger.setLevel(logging.DEBUG)
            logger.debug("Modo verbose ativado")
        
        # Verificar se o caminho do repositório é válido
        if not os.path.isdir(args.target):
            logger.error(f"FALHA - Diretório do repositório não encontrado: {args.target}")
            return
            
        git_dir = os.path.join(args.target, '.git')
        if not os.path.isdir(git_dir):
            logger.warning(f"AVISO - O diretório não é um repositório Git: {args.target}")
            # Continuamos a execução mesmo sem repositório Git
            # return
            
        # Mudar para o diretório do projeto
        os.chdir(args.target)
        logger.info(f"Trabalhando no diretório: {os.getcwd()}")
        
        # Log seguro das variáveis de ambiente e tokens
        if has_utils:
            # Usar utilitários avançados se disponíveis
            logger.info(f"Status do token GitHub: {get_env_status('GITHUB_TOKEN')}")
            logger.info(f"Status do token OpenAI: {get_env_status('OPENAI_API_KEY')}")
        else:
            # Simples verificação de presença
            github_token_status = 'configurado' if args.token else 'não configurado'
            openai_token_status = 'configurado' if args.openai_token else 'não configurado'
            logger.info(f"Status do token GitHub: {github_token_status}")
            logger.info(f"Status do token OpenAI: {openai_token_status}")
        
        if not args.token:
            logger.error("FALHA - Token GitHub ausente")
            return
            
        if not args.owner or not args.repo:
            logger.error("FALHA - Parâmetros owner/repo ausentes")
            return
        
        logger.info(f"Iniciando processo | Prompt: {args.prompt[:100]}...")
        
        agent = FeatureCreationAgent(args.token, args.owner, args.repo)
        validator = PlanValidator(logger)
        
        # Loop de auto-correção
        attempt = 0
        valid_plan = False
        current_plan = args.execution_plan
        
        while not valid_plan and attempt < args.max_attempts:
            attempt += 1
            logger.info(f"Tentativa {attempt} de {args.max_attempts}")
            
            # Validar plano
            validation_result = validator.validate(current_plan, args.openai_token)
            
            if validation_result.get("is_valid", False):
                valid_plan = True
                logger.info("Plano válido encontrado!")
            else:
                missing_items = validation_result.get("missing_items", [])
                # Mascarar possíveis dados sensíveis nos itens ausentes
                safe_missing_items = [mask_sensitive_data(item) for item in missing_items]
                logger.warning(f"Plano inválido. Itens ausentes: {safe_missing_items}")
                
                # Solicitar correção
                try:
                    corrected_plan = request_plan_correction(
                        args.prompt, 
                        current_plan, 
                        validation_result, 
                        args.openai_token,
                        args.config
                    )
                    current_plan = corrected_plan
                    logger.info("Plano corrigido recebido")
                except Exception as e:
                    # Mascarar dados sensíveis na mensagem de erro
                    error_msg = mask_sensitive_data(str(e))
                    logger.error(f"Erro ao corrigir plano: {error_msg}")
                    break
        
        # Executar com o plano final
        if valid_plan:
            logger.info("Executando com plano validado")
        else:
            logger.warning(f"Execução com plano parcial após {args.max_attempts} tentativas")
        
        # Executar a criação da feature
        result = agent.execute_feature_creation(args.prompt, current_plan, openai_token=args.openai_token)
        
        # Verificar resultado
        if isinstance(result, tuple) and len(result) == 2:
            # Resultado normal: (issue_number, branch_name)
            issue_number, branch_name = result
            logger.info(f"Processo de criação de feature concluído para issue #{issue_number}")
        elif isinstance(result, dict) and "status" in result:
            # Resultado de erro
            if result["status"] == "erro":
                logger.warning(f"Processo de criação de feature concluído com limitações: {result['mensagem']}")
            else:
                logger.info(f"Processo de criação de feature concluído com status: {result['status']}")
        else:
            logger.warning("Processo de criação de feature concluído com resultado desconhecido")
            
        logger.info("Processo de criação de feature concluído")
        
    except Exception as e:
        # Mascarar dados sensíveis na mensagem de erro
        error_msg = mask_sensitive_data(str(e))
        logger.error(f"FALHA - main | Erro: {error_msg}", exc_info=True)
        raise

@log_execution
def request_plan_correction(prompt, current_plan, validation_result, openai_token, config_file):
    """Solicita correção do plano usando a API da OpenAI e os requisitos do arquivo YAML"""
    from openai import OpenAI
    
    # Carregar requisitos do arquivo YAML
    requirements = {}
    req_details = ""
    
    try:
        if not os.path.exists(config_file):
            logger.warning(f"Arquivo de configuração não encontrado: {config_file}. Usando requisitos padrão.")
        else:
            with open(config_file, 'r', encoding='utf-8') as f:
                requirements = yaml.safe_load(f)
    except Exception as e:
        # Mascarar dados sensíveis na mensagem de erro
        error_msg = mask_sensitive_data(str(e))
        logger.warning(f"Erro ao carregar requisitos: {error_msg}. Usando requisitos padrão.")
    
    # Extrair detalhes dos requisitos para o prompt
    if "requisitos_entregaveis" in requirements:
        req_details = "Cada entregável deve incluir:\n"
        for req in requirements["requisitos_entregaveis"]:
            for key, desc in req.items():
                if key != "obrigatorio":
                    req_details += f"- {key}: {desc}\n"
    else:
        req_details = (
            "Cada entregável deve incluir: nome, descrição, dependências, "
            "exemplo de uso, critérios de aceitação, resolução de problemas "
            "e passos de implementação."
        )
    
    # Extrair itens ausentes - garantindo mascaramento
    missing_items = validation_result.get("missing_items", [])
    safe_missing_items = [mask_sensitive_data(item) for item in missing_items]
    missing_items_text = "\n".join([f"- {item}" for item in safe_missing_items])
    
    # Detalhes por entregável - garantindo mascaramento
    details_text = ""
    if "detalhes_por_entregavel" in validation_result:
        for entregavel in validation_result["detalhes_por_entregavel"]:
            nome = entregavel.get("nome", "Entregável sem nome")
            # Mascarar o nome se necessário
            nome_seguro = mask_sensitive_data(nome)
            itens = entregavel.get("itens_ausentes", [])
            safe_itens = [mask_sensitive_data(item) for item in itens]
            if safe_itens:
                details_text += f"\n### Para o entregável '{nome_seguro}':\n"
                details_text += "\n".join([f"- Falta: {item}" for item in safe_itens])
    
    # Criar mensagem de correção
    correction_message = (
        f"# Solicitação de Correção de Plano\n\n"
        f"## Prompt original:\n{prompt}\n\n"
        f"## Plano atual com problemas:\n{current_plan}\n\n"
        f"## Itens ausentes no plano:\n{missing_items_text}\n"
        f"{details_text}\n\n"
        f"## Requisitos para entregáveis:\n{req_details}\n\n"
        f"## Instruções:\n"
        f"Por favor, corrija o plano acima incluindo todos os itens ausentes. "
        f"Forneça o plano completo corrigido, não apenas os itens ausentes."
    )
    
    # Mascarar qualquer dado sensível que possa estar na mensagem
    safe_correction_message = mask_sensitive_data(correction_message)
    
    # Log seguro da operação (sem expor dados sensíveis)
    logger.info(f"Enviando solicitação de correção do plano (comprimento: {len(safe_correction_message)} caracteres)")
    
    # Chamar API para correção
    client = OpenAI(api_key=openai_token)
    
    response = client.chat.completions.create(
        model="gpt-4",  # Modelo mais avançado para correção
        messages=[
            {"role": "system", "content": "Você é um especialista em criar planos de execução de software."},
            {"role": "user", "content": safe_correction_message}
        ],
        temperature=0.7,
        max_tokens=4000
    )
    
    resposta = response.choices[0].message.content
    logger.info(f"Resposta recebida (comprimento: {len(resposta)} caracteres)")
    
    return resposta

if __name__ == "__main__":
    try:
        # Inicialização segura - usar a função de mascaramento já criada
        # em vez de fazer novo log, pois já mascaramos a linha de comando acima
        main()
    except KeyboardInterrupt:
        logger.warning("Processo interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        # Mascarar dados sensíveis no erro fatal
        error_msg = mask_sensitive_data(str(e))
        logger.critical(f"Erro fatal durante execução: {error_msg}", exc_info=True)
        sys.exit(1)
