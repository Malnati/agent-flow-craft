#!/usr/bin/env python3
"""
Script para iniciar o processo de criação de feature usando o FeatureCoordinatorAgent.
Este script recebe um prompt de texto e coordena a criação de uma feature completa.
"""

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
import asyncio

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
from core.logger import setup_logging, get_logger, log_execution, mask_sensitive_data

# Adicionar o diretório base ao path para permitir importações
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Importar o agente coordenador
from agents.agent_feature_coordinator import FeatureCoordinatorAgent

# Configurar logger
logger = get_logger(__name__)

# Mascaramento básico de dados sensíveis para logs
try:
    from core.utils import mask_sensitive_data, get_env_status
    has_utils = True
except ImportError:
    has_utils = False
    def mask_sensitive_data(data, mask_str='***'):
        if isinstance(data, str) and any(s in data.lower() for s in ['token', 'key', 'secret', 'password']):
            if len(data) > 10:
                return f"{data[:4]}{'*' * 12}{data[-4:] if len(data) > 8 else ''}"
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
    requirements_file = "src/configs/agents/plan_requirements.yaml"
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
def parse_arguments():
    """
    Analisa os argumentos da linha de comando.
    
    Returns:
        argparse.Namespace: Argumentos da linha de comando
    """
    parser = argparse.ArgumentParser(
        description="Inicia o processo de criação de feature usando o FeatureCoordinatorAgent",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "prompt",
        help="Descrição da feature a ser criada (texto ou caminho para arquivo .txt)"
    )
    
    parser.add_argument(
        "plan",
        nargs="?",
        default=None,
        help="Plano de execução opcional (texto ou caminho para arquivo .json/.txt)"
    )
    
    parser.add_argument(
        "--github_token",
        help="Token de acesso ao GitHub (opcional, usa variável de ambiente GITHUB_TOKEN se não especificado)"
    )
    
    parser.add_argument(
        "--openai_token",
        help="Token de acesso à OpenAI (opcional, usa variável de ambiente OPENAI_API_KEY se não especificado)"
    )
    
    parser.add_argument(
        "--owner",
        help="Proprietário do repositório GitHub (opcional, usa variável de ambiente GITHUB_OWNER se não especificado)"
    )
    
    parser.add_argument(
        "--repo",
        help="Nome do repositório GitHub (opcional, usa variável de ambiente GITHUB_REPO se não especificado)"
    )
    
    parser.add_argument(
        "--project_dir",
        dest="target",
        help="Diretório do projeto onde a feature será criada (opcional, usa diretório atual se não especificado)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=180,
        help="Timeout em segundos para operações (padrão: 180)"
    )
    
    parser.add_argument(
        "--output",
        help="Arquivo de saída para o resultado (opcional)"
    )
    
    parser.add_argument(
        "--context_dir",
        default="agent_context",
        help="Diretório para armazenar/acessar arquivos de contexto (padrão: agent_context)"
    )
    
    parser.add_argument(
        "--base_branch",
        default="main",
        help="Nome da branch base para criar a nova branch (padrão: main)"
    )
    
    return parser.parse_args()

@log_execution
async def main():
    """
    Função principal de execução do script.
    """
    # Configurar mascaramento de dados sensíveis
    _mask_sensitive_args()
    
    # Configurar logging específico
    feature_logger = setup_logging_for_feature_agent()
    
    try:
        # Analisar argumentos
        args = parse_arguments()
        masked_args = mask_args_for_logging(args)
        logger.info(f"Argumentos: {masked_args}")
        
        # Verificar e preparar arquivos de configuração
        config_files = ensure_config_files()
        
        # Verificar prompt - pode ser texto diretamente ou arquivo
        prompt_text = args.prompt
        if os.path.isfile(prompt_text):
            with open(prompt_text, 'r', encoding='utf-8') as f:
                prompt_text = f.read().strip()
            logger.info(f"Prompt carregado do arquivo: {args.prompt}")
        
        # Verificar plano - pode ser texto, arquivo JSON/TXT ou None
        execution_plan = None
        if args.plan:
            if os.path.isfile(args.plan):
                with open(args.plan, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    
                # Tentar interpretar como JSON
                try:
                    execution_plan = json.loads(content)
                    logger.info(f"Plano de execução carregado do arquivo JSON: {args.plan}")
                except json.JSONDecodeError:
                    # Se não for JSON, usar como texto
                    execution_plan = {"steps": [line.strip() for line in content.split('\n') if line.strip()]}
                    logger.info(f"Plano de execução carregado do arquivo de texto: {args.plan}")
            else:
                # Tentar interpretar como JSON
                try:
                    execution_plan = json.loads(args.plan)
                    logger.info("Plano de execução fornecido como JSON")
                except json.JSONDecodeError:
                    # Se não for JSON, usar como texto
                    execution_plan = {"steps": [line.strip() for line in args.plan.split('\n') if line.strip()]}
                    logger.info("Plano de execução fornecido como texto")
        
        # Verificar e criar diretório de contexto se necessário
        context_dir = Path(args.context_dir)
        if not context_dir.exists():
            context_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Diretório de contexto criado: {context_dir}")
        
        # Inicializar agente de criação de features
        agent = FeatureCoordinatorAgent(
            github_token=args.github_token,
            openai_token=args.openai_token,
            repo_owner=args.owner,
            repo_name=args.repo,
            target_dir=args.target,
            base_branch=args.base_branch
        )
        
        # Configurar o diretório de contexto do agente
        if hasattr(agent, 'context_dir'):
            agent.context_dir = context_dir
        
        # Executar criação de feature
        logger.info("Iniciando processo de criação de feature")
        feature_result = await agent.execute_feature_creation(
            prompt_text=prompt_text,
            execution_plan=execution_plan
        )
        
        # Verificar resultado
        if feature_result.get("status") == "error":
            logger.error(f"Erro na criação da feature: {feature_result.get('message')}")
            print(f"❌ Erro: {feature_result.get('message')}")
            sys.exit(1)
        
        # Extrair informações do resultado
        context_id = feature_result.get("context_id")
        issue_number = feature_result.get("issue_number")
        branch_name = feature_result.get("branch_name")
        
        # Exibir resultado
        print("\n🎉 Feature criada com sucesso!\n")
        print(f"📋 ID de Contexto: {context_id}")
        print(f"🔢 Issue: #{issue_number}")
        print(f"🌿 Branch: {branch_name}")
        
        # Salvar resultado se solicitado
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(feature_result, f, indent=2)
            print(f"\n💾 Resultado salvo em: {args.output}")
        
        logger.info(f"Processo concluído com sucesso: Issue #{issue_number}, Branch {branch_name}")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("Processo interrompido pelo usuário")
        print("\n⚠️  Processo interrompido pelo usuário")
        return 130
        
    except Exception as e:
        logger.error(f"Erro no processo de criação de feature: {str(e)}", exc_info=True)
        print(f"\n❌ Erro: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
