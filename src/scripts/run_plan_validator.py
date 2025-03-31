#!/usr/bin/env python3
"""
Script para executar o PlanValidator diretamente.
Valida um plano de execução para garantir que ele siga os requisitos definidos.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from src.core.core.logger import get_logger, log_execution

# Adicionar o diretório base ao path para permitir importações
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Importar o validador de planos
from apps.agent_manager.agents import PlanValidator

# Configurar logger
logger = get_logger(__name__)

# Mascaramento básico de dados sensíveis para logs
try:
    from src.core.core.utils import mask_sensitive_data, get_env_status
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
        description="Executa o PlanValidator para validar planos de execução",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "plan_file",
        help="Caminho para o arquivo JSON ou texto contendo o plano a ser validado"
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
        "--requirements",
        help="Arquivo com requisitos específicos para validação (opcional)"
    )
    
    parser.add_argument(
        "--output",
        help="Arquivo de saída para o resultado da validação (opcional)"
    )
    
    parser.add_argument(
        "--context_dir",
        default="agent_context",
        help="Diretório para armazenar/acessar arquivos de contexto (padrão: agent_context)"
    )
    
    parser.add_argument(
        "--project_dir",
        help="Diretório do projeto onde o plano será aplicado (opcional)"
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
        
        # Verificar arquivo de plano
        if not os.path.isfile(args.plan_file):
            logger.error(f"Arquivo de plano não encontrado: {args.plan_file}")
            print(f"❌ Erro: Arquivo de plano não encontrado: {args.plan_file}")
            return 1
            
        # Carregar plano do arquivo
        with open(args.plan_file, 'r', encoding='utf-8') as f:
            plan_content = f.read().strip()
            
        # Verificar requisitos específicos
        requirements_content = None
        if args.requirements:
            if os.path.isfile(args.requirements):
                with open(args.requirements, 'r', encoding='utf-8') as f:
                    requirements_content = f.read().strip()
                logger.info(f"Requisitos carregados do arquivo: {args.requirements}")
            else:
                logger.warning(f"Arquivo de requisitos não encontrado: {args.requirements}")
                
        # Verificar e criar diretório de contexto se necessário
        context_dir = Path(args.context_dir)
        if not context_dir.exists():
            context_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Diretório de contexto criado: {context_dir}")
            
        # Verificar diretório do projeto se fornecido
        if args.project_dir:
            project_dir = Path(args.project_dir)
            if not project_dir.exists():
                logger.warning(f"Diretório de projeto não encontrado: {project_dir}")
            else:
                logger.info(f"Utilizando diretório de projeto: {project_dir}")
        
        # Inicializar validador de planos
        openai_token = args.openai_token or os.environ.get('OPENAI_API_KEY', '')
        if not openai_token:
            logger.warning("Token OpenAI não fornecido. Algumas funcionalidades podem estar limitadas.")
            
        validator = PlanValidator()
        
        # Configurar diretório de contexto se o validador suportar
        if hasattr(validator, 'context_dir'):
            validator.context_dir = context_dir
            
        # Validar plano
        logger.info("Validando plano...")
        result = validator.validate(plan_content, openai_token, requirements=requirements_content, model=args.model)
        
        # Verificar resultado
        is_valid = result.get("valid", False)
        validation_score = result.get("score", 0)
        issues = result.get("issues", [])
        suggestions = result.get("suggestions", [])
        
        # Exibir resultado
        print("\n🔍 Resultado da validação:\n")
        print(f"✅ Plano válido: {'Sim' if is_valid else 'Não'}")
        print(f"🏆 Pontuação: {validation_score}/10")
        
        if issues:
            print("\n⚠️ Problemas encontrados:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
                
        if suggestions:
            print("\n💡 Sugestões de melhoria:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
                
        print(f"\n📊 Avaliação: {result.get('evaluation', 'Não avaliado')}")
        
        # Salvar resultado se solicitado
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultado salvo em: {args.output}")
        
        # Retorno bem-sucedido (mesmo se o plano não for válido)
        return 0
        
    except KeyboardInterrupt:
        logger.warning("Processo interrompido pelo usuário")
        print("\n⚠️  Processo interrompido pelo usuário")
        return 130
        
    except Exception as e:
        logger.error(f"Erro ao validar plano: {str(e)}", exc_info=True)
        print(f"\n❌ Erro: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 