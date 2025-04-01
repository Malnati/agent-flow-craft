#!/usr/bin/env python3
"""
Script de inicialização para o FeatureAgent.
Este script recebe um prompt e coordena o processo de criação de feature.
"""

import os
import sys
import argparse
from pathlib import Path
import logging
import json

# Adicionar o diretório base ao path para permitir importações
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Importar o agente de feature
from agents import FeatureCoordinatorAgent

# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FeatureAgent")

def parse_arguments():
    """
    Analisa os argumentos da linha de comando.
    
    Returns:
        argparse.Namespace: Argumentos da linha de comando
    """
    parser = argparse.ArgumentParser(
        description="Inicia o processo de criação de feature usando o FeatureAgent",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "prompt",
        help="Descrição da feature a ser criada"
    )
    
    parser.add_argument(
        "--project_dir",
        help="Diretório do projeto onde a feature será criada (opcional, usa diretório atual se não especificado)"
    )
    
    parser.add_argument(
        "--output",
        help="Arquivo de saída para o resultado (opcional)"
    )
    
    parser.add_argument(
        "--context_dir",
        default="agent_context",
        help="Diretório para armazenar arquivos de contexto (padrão: agent_context)"
    )
    
    parser.add_argument(
        "--github_token",
        help="Token de acesso ao GitHub (opcional, usa variável de ambiente GITHUB_TOKEN se não especificado)"
    )
    
    parser.add_argument(
        "--openai_token",
        help="Token de acesso à API da OpenAI (opcional, usa variável de ambiente OPENAI_API_KEY se não especificado)"
    )
    
    parser.add_argument(
        "--model",
        default="gpt-4-turbo",
        help="Modelo da OpenAI a ser utilizado (padrão: gpt-4-turbo)"
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
        if 'github_token' in masked_args and masked_args['github_token']:
            if len(masked_args['github_token']) > 10:
                masked_args['github_token'] = f"{masked_args['github_token'][:4]}{'*' * 12}{masked_args['github_token'][-4:]}"
            else:
                masked_args['github_token'] = "***"
        if 'openai_token' in masked_args and masked_args['openai_token']:
            if len(masked_args['openai_token']) > 10:
                masked_args['openai_token'] = f"{masked_args['openai_token'][:4]}{'*' * 12}{masked_args['openai_token'][-4:]}"
            else:
                masked_args['openai_token'] = "***"
        
        logger.info(f"Argumentos: {masked_args}")
        
        # Inicializar tokens
        github_token = args.github_token or os.environ.get('GITHUB_TOKEN', '')
        openai_token = args.openai_token or os.environ.get('OPENAI_API_KEY', '')
        
        # Verificar tokens
        if not github_token:
            logger.warning("Token GitHub não fornecido. Algumas funcionalidades podem estar limitadas.")
        if not openai_token:
            logger.warning("Token OpenAI não fornecido. Algumas funcionalidades podem estar limitadas.")
        
        # Verificar diretório do projeto
        project_dir = args.project_dir or os.getcwd()
        if not os.path.exists(project_dir):
            logger.error(f"Diretório do projeto não encontrado: {project_dir}")
            print(f"❌ Erro: Diretório do projeto não encontrado: {project_dir}")
            return 1
        
        # Verificar e criar diretório de contexto
        context_dir = Path(args.context_dir)
        if not context_dir.exists():
            context_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Diretório de contexto criado: {context_dir}")
        
        # Inicializar agente de feature
        agent = FeatureCoordinatorAgent(
            github_token=github_token,
            openai_token=openai_token,
            target_dir=project_dir
        )
        
        # Configurar o diretório de contexto do agente
        if hasattr(agent, 'context_dir'):
            agent.context_dir = context_dir
        elif hasattr(agent, 'set_context_dir'):
            agent.set_context_dir(str(context_dir))
        
        # Executar a criação da feature
        logger.info(f"Iniciando criação da feature com prompt: {args.prompt}")
        print(f"\n🚀 Iniciando criação da feature: '{args.prompt}'")
        print(f"⚙️  Modelo OpenAI: {args.model} (será usado por agentes internos)")
        
        # Se o agente concept_agent suportar o modelo, configurar
        if hasattr(agent, 'concept_agent') and hasattr(agent.concept_agent, 'set_model'):
            agent.concept_agent.set_model(args.model)
            logger.info(f"Modelo configurado para ConceptAgent: {args.model}")
        
        # Chamar o método de criação de feature
        result = agent.create_feature(args.prompt)
        
        # Verificar resultado
        if isinstance(result, dict) and result.get("status") == "error":
            logger.error(f"Erro ao criar feature: {result.get('message')}")
            print(f"❌ Erro: {result.get('message')}")
            return 1
        
        # Exibir resultado
        print("\n✅ Feature criada com sucesso!\n")
        if isinstance(result, dict):
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(result)
        
        # Salvar resultado se solicitado
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                if isinstance(result, dict):
                    json.dump(result, f, indent=2, ensure_ascii=False)
                else:
                    f.write(str(result))
            print(f"\n💾 Resultado salvo em: {args.output}")
        
        # Retorno bem-sucedido
        return 0
        
    except KeyboardInterrupt:
        logger.warning("Processo interrompido pelo usuário")
        print("\n⚠️  Processo interrompido pelo usuário")
        return 130
        
    except Exception as e:
        logger.error(f"Erro ao criar feature: {str(e)}", exc_info=True)
        print(f"\n❌ Erro: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 