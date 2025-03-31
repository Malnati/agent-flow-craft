#!/usr/bin/env python3
"""
Script para executar o TDDCriteriaAgent diretamente.
Gera critérios de aceitação TDD para features a partir de um conceito gerado anteriormente.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from core.core.logger import get_logger, log_execution

# Adicionar o diretório base ao path para permitir importações
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Importar o agente de critérios TDD
from apps.agent_manager.agents import TDDCriteriaAgent

# Configurar logger
logger = get_logger(__name__)

# Mascaramento básico de dados sensíveis para logs
try:
    from core.core.utils import mask_sensitive_data, get_env_status
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
        description="Executa o TDDCriteriaAgent para gerar critérios de aceitação TDD",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "context_id",
        help="ID do contexto do conceito de feature a ser utilizado"
    )
    
    parser.add_argument(
        "--project_dir", 
        help="Diretório do projeto onde serão buscados arquivos de código-fonte (obrigatório)",
        required=True
    )
    
    parser.add_argument(
        "--openai_token",
        help="Token de acesso à OpenAI (opcional, usa variável de ambiente OPENAI_API_KEY se não especificado)"
    )
    
    parser.add_argument(
        "--model",
        default="gpt-4-turbo",
        help="Modelo da OpenAI a ser utilizado (padrão: gpt-4-turbo)"
    )
    
    parser.add_argument(
        "--output",
        help="Arquivo de saída para os critérios TDD gerados (opcional)"
    )
    
    parser.add_argument(
        "--context_dir",
        default="agent_context",
        help="Diretório para armazenar/acessar arquivos de contexto (padrão: agent_context)"
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
        if args.openai_token:
            if len(args.openai_token) > 10:
                masked_args["openai_token"] = f"{args.openai_token[:4]}{'*' * 12}{args.openai_token[-4:] if len(args.openai_token) > 8 else ''}"
            else:
                masked_args["openai_token"] = "***"
        
        logger.info(f"Argumentos: {masked_args}")
        
        # Verificar se o diretório do projeto existe
        project_dir = Path(args.project_dir)
        if not project_dir.exists() or not project_dir.is_dir():
            logger.error(f"Diretório do projeto não encontrado: {args.project_dir}")
            print(f"\n❌ Erro: Diretório do projeto não encontrado: {args.project_dir}")
            return 1
        
        # Verificar e criar diretório de contexto se necessário
        context_dir = Path(args.context_dir)
        if not context_dir.exists():
            context_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Diretório de contexto criado: {context_dir}")
        
        # Configurar diretório de contexto
        logger.info(f"Utilizando diretório de contexto: {context_dir} (absoluto: {context_dir.resolve()})")
        
        # Inicializar agente de critérios TDD
        openai_token = args.openai_token or os.environ.get('OPENAI_API_KEY', '')
        if not openai_token:
            logger.warning("Token OpenAI não fornecido. Algumas funcionalidades podem estar limitadas.")
            
        # Inicializar o agente com o diretório de contexto personalizado
        agent = TDDCriteriaAgent(openai_token=openai_token, model=args.model)
        agent.context_dir = context_dir
        logger.info(f"Diretório de contexto do agente configurado: {agent.context_dir}")
        logger.info(f"Modelo OpenAI configurado: {args.model}")
        
        # Verificar se o context_id existe
        context_file = context_dir / f"{args.context_id}.json"
        if not context_file.exists():
            logger.error(f"Arquivo de contexto não encontrado: {context_file}")
            print(f"\n❌ Erro: Contexto '{args.context_id}' não encontrado no diretório {context_dir}")
            return 1
            
        # Gerar critérios TDD
        logger.info(f"Gerando critérios TDD para o conceito: {args.context_id}")
        criteria = agent.generate_tdd_criteria(args.context_id, args.project_dir)
        
        # Exibir critérios
        print("\n🧪 Critérios de aceitação TDD gerados:\n")
        print(json.dumps(criteria, indent=2, ensure_ascii=False))
        
        # Salvar critérios se solicitado
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(criteria, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Critérios salvos em: {args.output}")
        
        # Retorno bem-sucedido
        return 0
        
    except KeyboardInterrupt:
        logger.warning("Processo interrompido pelo usuário")
        print("\n⚠️  Processo interrompido pelo usuário")
        return 130
        
    except Exception as e:
        logger.error(f"Erro ao gerar critérios TDD: {str(e)}", exc_info=True)
        print(f"\n❌ Erro: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 