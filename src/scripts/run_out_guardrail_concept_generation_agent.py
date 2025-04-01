#!/usr/bin/env python3
"""
Script para execução direta do OutGuardrailConceptGenerationAgent.
Analisa e melhora conceitos de feature previamente gerados pelo ConceptGenerationAgent.
"""

import os
import sys
import json
import time
import argparse
import asyncio
from pathlib import Path
from datetime import datetime

# Adicionar diretório raiz ao path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from core.logger import get_logger
from agents import OutGuardrailConceptGenerationAgent

# Configuração do logger
logger = get_logger(__name__)

# Função para mascarar dados sensíveis em logs
def mask_data(data):
    masked_data = data.copy() if isinstance(data, dict) else {}
    if isinstance(data, dict) and 'openai_token' in data:
        masked_data['openai_token'] = f"{data['openai_token'][:4]}...{data['openai_token'][-4:]}" if data['openai_token'] else None
    return masked_data

def parse_arguments():
    """
    Analisa os argumentos da linha de comando.
    
    Returns:
        argparse.Namespace: Argumentos da linha de comando
    """
    parser = argparse.ArgumentParser(
        description="Executa o OutGuardrailConceptGenerationAgent para avaliar e melhorar conceitos de features."
    )
    
    # Argumentos obrigatórios
    parser.add_argument(
        "concept_id",
        help="ID do conceito a ser avaliado/melhorado"
    )
    
    parser.add_argument(
        "prompt",
        help="Prompt original usado para gerar o conceito"
    )
    
    # Argumentos opcionais com flags
    parser.add_argument(
        "--project_dir",
        help="Diretório do projeto para análise do código-fonte (opcional)"
    )
    
    parser.add_argument(
        "--openai_token",
        help="Token de acesso à API da OpenAI (opcional se definido como variável de ambiente)"
    )
    
    parser.add_argument(
        "--model",
        default="gpt-4-turbo",
        help="Modelo da OpenAI a ser usado (padrão: gpt-4-turbo)"
    )
    
    parser.add_argument(
        "--elevation_model",
        help="Modelo alternativo para elevação em caso de melhoria (opcional)"
    )
    
    parser.add_argument(
        "--output",
        help="Arquivo de saída para o conceito avaliado/melhorado (opcional)"
    )
    
    parser.add_argument(
        "--context_dir",
        default="agent_context",
        help="Diretório para armazenar/acessar arquivos de contexto (padrão: agent_context)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignora a validação e passa o conceito adiante sem modificações"
    )
    
    parser.add_argument(
        "--async",
        dest="is_async",
        action="store_true",
        help="Executa o guardrail de forma assíncrona"
    )
    
    return parser.parse_args()

async def run_async(args):
    """
    Executa o OutGuardrailConceptGenerationAgent de forma assíncrona.
    
    Args:
        args: Argumentos da linha de comando
        
    Returns:
        dict: Resultado da execução do guardrail
    """
    logger.info("INÍCIO - run_async")
    
    try:
        # Inicializar o agente guardrail
        guardrail_agent = OutGuardrailConceptGenerationAgent(
            openai_token=args.openai_token,
            model=args.model
        )
        
        # Configurar diretório de contexto
        guardrail_agent.context_dir = Path(args.context_dir)
        logger.info(f"Diretório de contexto configurado: {args.context_dir}")
        
        logger.info("Executando OutGuardrailConceptGenerationAgent de forma assíncrona...")
        
        # Como o método não é assíncrono nativamente, usamos run_in_executor
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: guardrail_agent.execute_concept_guardrail(
                concept_id=args.concept_id,
                prompt=args.prompt,
                project_dir=args.project_dir,
                elevation_model=args.elevation_model,
                force=args.force
            )
        )
        
        return result
    except Exception as e:
        logger.error(f"Erro ao executar OutGuardrailConceptGenerationAgent: {e}")
        return {"error": str(e)}

def run_sync(args):
    """
    Executa o OutGuardrailConceptGenerationAgent de forma síncrona.
    
    Args:
        args: Argumentos da linha de comando
        
    Returns:
        dict: Resultado da execução do guardrail
    """
    logger.info("INÍCIO - run_sync")
    
    try:
        # Inicializar o agente guardrail
        guardrail_agent = OutGuardrailConceptGenerationAgent(
            openai_token=args.openai_token,
            model=args.model
        )
        
        # Configurar diretório de contexto
        guardrail_agent.context_dir = Path(args.context_dir)
        logger.info(f"Diretório de contexto configurado: {args.context_dir}")
        
        logger.info("Executando OutGuardrailConceptGenerationAgent...")
        result = guardrail_agent.execute_concept_guardrail(
            concept_id=args.concept_id,
            prompt=args.prompt,
            project_dir=args.project_dir,
            elevation_model=args.elevation_model,
            force=args.force
        )
        
        return result
    except Exception as e:
        logger.error(f"Erro ao executar OutGuardrailConceptGenerationAgent: {e}")
        return {"error": str(e)}

def main():
    """
    Função principal que executa o OutGuardrailConceptGenerationAgent.
    
    Returns:
        int: Código de saída (0 para sucesso, 1 para erro)
    """
    logger.info("INÍCIO - main")
    
    try:
        args = parse_arguments()
        # Mascarar tokens sensíveis
        masked_args = vars(args).copy()
        if args.openai_token:
            masked_args['openai_token'] = f"{args.openai_token[:4]}{'*' * 8}{args.openai_token[-4:] if len(args.openai_token) > 8 else ''}"
            
        logger.info(f"Iniciando OutGuardrailConceptGenerationAgent com argumentos: {masked_args}")
        
        # Criar diretório de contexto se não existir
        Path(args.context_dir).mkdir(exist_ok=True)
        
        # Se modo assíncrono, usar asyncio
        if args.is_async:
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(run_async(args))
        else:
            result = run_sync(args)
        
        # Verificar erros
        if "error" in result:
            logger.error(f"Erro ao executar OutGuardrailConceptGenerationAgent: {result.get('error')}")
            if "raw_content" in result:
                logger.warning(f"Conteúdo bruto retornado: {result['raw_content'][:100]}...")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 1
        
        # Verificar se foi usado modo force
        if result.get("force_mode"):
            logger.info("Conceito passado sem validação (modo force ativado)")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
        
        # Verificar avaliação
        evaluation = result.get("evaluation", {})
        logger.info(f"Avaliação do conceito - Score: {evaluation.get('score')}/10")
        
        if evaluation.get("issues"):
            logger.info("Problemas identificados:")
            for issue in evaluation.get("issues", []):
                logger.info(f"- {issue}")
        
        if result.get("was_improved"):
            logger.info("Conceito foi melhorado com sucesso")
            logger.info(f"ID do conceito melhorado: {result.get('improved_concept_id')}")
            
            # Mostrar melhoria na avaliação, se disponível
            if "improved_evaluation" in result:
                improved_eval = result["improved_evaluation"]
                logger.info(f"Avaliação melhorada - Score: {improved_eval.get('score')}/10 " +
                           f"(anterior: {evaluation.get('score')}/10)")
        else:
            logger.info(f"Conceito não foi modificado: {result.get('message', 'Nenhuma melhoria necessária')}")
        
        # Exibir conceito final
        concept = result.get("concept", {})
        print("\n🧠 Conceito final:\n")
        print(json.dumps(concept, indent=2, ensure_ascii=False))
        
        # Salvar resultado em arquivo de saída, se especificado
        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                logger.info(f"Resultado salvo em: {args.output}")
            except Exception as e:
                logger.error(f"Erro ao salvar resultado em {args.output}: {e}")
        
        logger.info("OutGuardrailConceptGenerationAgent concluído com sucesso")
        return 0
    except Exception as e:
        logger.error(f"Erro ao executar OutGuardrailConceptGenerationAgent: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 