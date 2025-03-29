#!/usr/bin/env python3
"""
Script para executar o GitHubIntegrationAgent diretamente.
Processa um conceito de feature previamente gerado para criar issue, branch e PR no GitHub.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from agent_platform.core.logger import get_logger, log_execution

# Adicionar o diretório base ao path para permitir importações
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Importar o agente GitHub
from apps.agent_manager.agents import GitHubIntegrationAgent

# Configurar logger
logger = get_logger(__name__)

# Mascaramento básico de dados sensíveis para logs
try:
    from agent_platform.core.utils import mask_sensitive_data, get_env_status
    has_utils = True
except ImportError:
    has_utils = False
    def mask_sensitive_data(data, mask_str='***'):
        if isinstance(data, str) and any(s in data.lower() for s in ['token', 'key', 'secret', 'password']):
            if len(data) > 10:
                return f"{data[:4]}{'*' * 12}{data[-4:] if len(data) > 8 else ''}"
            return mask_str
        return data

@log_execution
def parse_arguments():
    """
    Analisa os argumentos da linha de comando.
    
    Returns:
        argparse.Namespace: Argumentos da linha de comando
    """
    parser = argparse.ArgumentParser(
        description="Executa o GitHubIntegrationAgent para processar um conceito de feature",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "context_id",
        help="ID do contexto a ser processado (ex: feature_concept_20240328_123456)"
    )
    
    parser.add_argument(
        "--github_token",
        help="Token de acesso ao GitHub (opcional, usa variável de ambiente GITHUB_TOKEN se não especificado)"
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
        "--target",
        help="Diretório alvo do repositório Git (opcional, usa diretório atual se não especificado)"
    )
    
    parser.add_argument(
        "--output",
        help="Arquivo de saída para o resultado (opcional)"
    )
    
    return parser.parse_args()

def main():
    """
    Função principal de execução do script.
    """
    try:
        # Analisar argumentos
        args = parse_arguments()
        
        # Mascarar dados sensíveis para logging
        masked_args = vars(args).copy()
        if args.github_token:
            if len(args.github_token) > 10:
                masked_args["github_token"] = f"{args.github_token[:4]}{'*' * 12}{args.github_token[-4:] if len(args.github_token) > 8 else ''}"
            else:
                masked_args["github_token"] = "***"
        
        logger.info(f"Argumentos: {masked_args}")
        
        # Inicializar agente GitHub
        github_token = args.github_token or os.environ.get('GITHUB_TOKEN', '')
        repo_owner = args.owner or os.environ.get('GITHUB_OWNER', '')
        repo_name = args.repo or os.environ.get('GITHUB_REPO', '')
        target_dir = args.target
        
        if not github_token:
            logger.warning("Token GitHub não fornecido. Algumas funcionalidades podem estar limitadas.")
            
        agent = GitHubIntegrationAgent(
            github_token=github_token,
            repo_owner=repo_owner,
            repo_name=repo_name,
            target_dir=target_dir
        )
        
        # Processar conceito
        logger.info(f"Processando conceito do contexto: {args.context_id}")
        result = agent.process_concept(args.context_id)
        
        # Verificar resultado
        if result.get("status") == "error":
            logger.error(f"Erro ao processar conceito: {result.get('message')}")
            print(f"❌ Erro: {result.get('message')}")
            return 1
        
        # Exibir resultado
        print("\n🚀 Integração GitHub concluída:\n")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Extrair informações
        issue_number = result.get("issue_number")
        branch_name = result.get("branch_name")
        branch_created = result.get("branch_created")
        plan_created = result.get("plan_created")
        pr_created = result.get("pr_created")
        
        # Exibir resumo
        print("\n📋 Resumo:")
        print(f"🔢 Issue: #{issue_number}")
        print(f"🌿 Branch: {branch_name}")
        print(f"✅ Branch criada: {'Sim' if branch_created else 'Não'}")
        print(f"✅ Plano criado: {'Sim' if plan_created else 'Não'}")
        print(f"✅ PR criado: {'Sim' if pr_created else 'Não'}")
        
        # Salvar resultado se solicitado
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultado salvo em: {args.output}")
        
        # Retorno bem-sucedido
        return 0
        
    except KeyboardInterrupt:
        logger.warning("Processo interrompido pelo usuário")
        print("\n⚠️  Processo interrompido pelo usuário")
        return 130
        
    except Exception as e:
        logger.error(f"Erro ao processar conceito: {str(e)}", exc_info=True)
        print(f"\n❌ Erro: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 