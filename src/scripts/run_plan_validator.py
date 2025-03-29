#!/usr/bin/env python3
"""
Script para executar o PlanValidator diretamente.
Valida planos de execução de features verificando se atendem aos requisitos.
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

# Importar o validador de planos
from apps.agent_manager.agents import PlanValidator

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
        description="Executa o PlanValidator para validar planos de execução",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "plan_file",
        help="Arquivo com o plano de execução a ser validado (JSON ou TXT)"
    )
    
    parser.add_argument(
        "--requirements",
        help="Arquivo YAML com requisitos de validação (opcional)"
    )
    
    parser.add_argument(
        "--openai_token",
        help="Token de acesso à OpenAI (opcional, usa variável de ambiente OPENAI_API_KEY se não especificado)"
    )
    
    parser.add_argument(
        "--output",
        help="Arquivo de saída para o resultado da validação (opcional)"
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
            raise ValueError(f"Arquivo de plano não encontrado: {args.plan_file}")
            
        # Ler conteúdo do plano
        with open(args.plan_file, 'r', encoding='utf-8') as f:
            plan_content = f.read().strip()
            
        # Verificar se o conteúdo parece ser JSON
        try:
            json.loads(plan_content)
            logger.info("Plano detectado como JSON")
        except json.JSONDecodeError:
            logger.info("Plano não está em formato JSON válido. Tratando como texto.")
        
        # Inicializar validador
        validator = PlanValidator(requirements_file=args.requirements)
        
        # Obter token da OpenAI
        openai_token = args.openai_token or os.environ.get('OPENAI_API_KEY', '')
        if not openai_token:
            logger.warning("Token OpenAI não fornecido. Validação pode ser limitada.")
            
        # Validar plano
        logger.info("Validando plano de execução...")
        result = validator.validate(plan_content, openai_token)
        
        # Exibir resultado
        is_valid = result.get("is_valid", False)
        missing_items = result.get("missing_items", [])
        
        print("\n🔍 Resultado da validação:\n")
        print(f"✅ Plano válido: {'Sim' if is_valid else 'Não'}")
        
        if not is_valid:
            print(f"\n❌ Itens ausentes ({len(missing_items)}):")
            for item in missing_items:
                print(f"- {item}")
            
            if "detalhes_por_entregavel" in result:
                print("\n📋 Detalhes por entregável:")
                for entregavel in result["detalhes_por_entregavel"]:
                    nome = entregavel.get("nome", "Entregável sem nome")
                    itens = entregavel.get("itens_ausentes", [])
                    if itens:
                        print(f"\n=> {nome}:")
                        for item in itens:
                            print(f"  - {item}")
        
        # Salvar resultado se solicitado
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultado salvo em: {args.output}")
        
        # Retorno com base na validade
        return 0 if is_valid else 2
        
    except ValueError as e:
        logger.error(f"Erro de validação: {str(e)}")
        print(f"\n❌ Erro: {str(e)}")
        return 1
        
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