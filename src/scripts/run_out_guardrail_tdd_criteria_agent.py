#!/usr/bin/env python3
"""
Script para execução direta do OutGuardrailTDDCriteriaAgent.
Analisa e melhora critérios TDD previamente gerados pelo TDDCriteriaAgent.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from core.core.logger import get_logger
from apps.agent_manager.agents import OutGuardrailTDDCriteriaAgent

# Configuração do logger
logger = get_logger(__name__)

def parse_arguments():
    """
    Analisa os argumentos da linha de comando.
    
    Returns:
        argparse.Namespace: Argumentos da linha de comando
    """
    parser = argparse.ArgumentParser(
        description="Executa o OutGuardrailTDDCriteriaAgent para avaliar e melhorar critérios TDD."
    )
    
    parser.add_argument(
        "criteria_id",
        help="ID do contexto dos critérios TDD a serem avaliados"
    )
    
    parser.add_argument(
        "concept_id",
        help="ID do contexto do conceito associado aos critérios"
    )
    
    parser.add_argument(
        "--project_dir",
        default=os.getcwd(),
        help="Diretório do projeto para análise (opcional)"
    )
    
    parser.add_argument(
        "--context_dir",
        default="agent_context",
        help="Diretório para armazenar arquivos de contexto (padrão: agent_context)"
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
        help="Arquivo de saída para o resultado (opcional)"
    )
    
    return parser.parse_args()

def main():
    """
    Função principal que executa o OutGuardrailTDDCriteriaAgent.
    
    Returns:
        int: Código de saída (0 para sucesso, 1 para erro)
    """
    try:
        # Obter argumentos da linha de comando
        args = parse_arguments()
        
        # Mascarar dados sensíveis para logging
        masked_args = vars(args).copy()
        if args.openai_token:
            masked_args["openai_token"] = f"{args.openai_token[:4]}{'*' * 8}{args.openai_token[-4:] if len(args.openai_token) > 8 else ''}"
        
        logger.info(f"Iniciando OutGuardrailTDDCriteriaAgent com argumentos: {masked_args}")
        
        # Criar diretório de contexto se não existir
        context_dir = Path(args.context_dir)
        context_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar o agente guardrail
        guardrail_agent = OutGuardrailTDDCriteriaAgent(
            openai_token=args.openai_token or os.environ.get("OPENAI_API_KEY", ""),
            model=args.model
        )
        
        # Configurar o diretório de contexto do agente
        guardrail_agent.context_dir = context_dir
        logger.info(f"Diretório de contexto configurado: {args.context_dir}")
        
        # Executar o guardrail
        logger.info("Executando OutGuardrailTDDCriteriaAgent...")
        result = guardrail_agent.execute_tdd_guardrail(
            criteria_id=args.criteria_id,
            concept_id=args.concept_id,
            project_dir=args.project_dir
        )
        
        # Exibir resultado
        print(json.dumps(result, indent=2))
        
        # Salvar resultado se solicitado
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logger.info(f"Resultado salvo em: {args.output}")
            
        logger.info("OutGuardrailTDDCriteriaAgent concluído com sucesso")
        return 0
        
    except Exception as e:
        logger.error(f"Erro ao executar OutGuardrailTDDCriteriaAgent: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 