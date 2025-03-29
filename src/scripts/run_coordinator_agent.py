#!/usr/bin/env python3
"""
Script para executar o FeatureCoordinatorAgent diretamente.
Coordena a criação de uma feature com base em um prompt ou plano existente.
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

# Importar o agente coordenador
from apps.agent_manager.agents import FeatureCoordinatorAgent
from apps.agent_manager.agents.context_manager import ContextManager

# Configurar logger
logger = get_logger(__name__)

@log_execution
def parse_arguments():
    """
    Analisa os argumentos da linha de comando.
    
    Returns:
        argparse.Namespace: Argumentos da linha de comando
    """
    parser = argparse.ArgumentParser(
        description="Executa o FeatureCoordinatorAgent para criar uma feature",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "prompt",
        help="Descrição da feature a ser criada"
    )
    
    parser.add_argument(
        "--plan_file",
        help="Arquivo JSON contendo o plano de execução (opcional)"
    )
    
    parser.add_argument(
        "--project_dir", 
        dest="target",
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
        if args.github_token:
            masked_args["github_token"] = f"{args.github_token[:4]}{'*' * 12}{args.github_token[-4:]}"
        if args.openai_token:
            masked_args["openai_token"] = f"{args.openai_token[:4]}{'*' * 12}{args.openai_token[-4:]}"
        
        logger.info(f"Argumentos: {masked_args}")
        
        # Inicializar tokens a partir dos argumentos ou variáveis de ambiente
        github_token = args.github_token or os.environ.get('GITHUB_TOKEN', '')
        openai_token = args.openai_token or os.environ.get('OPENAI_API_KEY', '')
        
        if not github_token:
            logger.warning("Token GitHub não fornecido. Algumas funcionalidades podem estar limitadas.")
        
        if not openai_token:
            logger.warning("Token OpenAI não fornecido. Algumas funcionalidades podem estar limitadas.")
        
        # Verificar diretório do projeto
        target_dir = args.target or os.getcwd()
        if not Path(target_dir).exists():
            logger.error(f"Diretório do projeto não encontrado: {target_dir}")
            print(f"❌ Erro: Diretório do projeto não encontrado: {target_dir}")
            return 1
        
        # Verificar e criar diretório de contexto se necessário
        context_dir = Path(args.context_dir)
        if not context_dir.exists():
            context_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Diretório de contexto criado: {context_dir}")
        
        # Inicializar gerenciador de contexto com o diretório personalizado
        context_manager = ContextManager(base_dir=str(context_dir))
        
        # Inicializar agente coordenador
        agent = FeatureCoordinatorAgent(
            openai_token=openai_token,
            github_token=github_token,
            target_dir=target_dir
        )
        
        # Configurar o diretório de contexto do agente
        if hasattr(agent, 'context_dir'):
            agent.context_dir = context_dir
        elif hasattr(agent, 'set_context_dir'):
            agent.set_context_dir(str(context_dir))
            
        # Configurar o modelo, se possível
        if hasattr(agent, 'concept_agent') and hasattr(agent.concept_agent, 'set_model'):
            agent.concept_agent.set_model(args.model)
            logger.info(f"Modelo configurado para ConceptAgent: {args.model}")
        
        # Carregar plano de execução se especificado
        execution_plan = None
        if args.plan_file:
            plan_path = Path(args.plan_file)
            if not plan_path.exists():
                logger.error(f"Arquivo de plano não encontrado: {args.plan_file}")
                print(f"❌ Erro: Arquivo de plano não encontrado: {args.plan_file}")
                return 1
                
            try:
                with open(plan_path, 'r', encoding='utf-8') as f:
                    execution_plan = json.load(f)
                logger.info(f"Plano de execução carregado de: {args.plan_file}")
            except Exception as e:
                logger.error(f"Erro ao carregar arquivo de plano: {str(e)}")
                print(f"❌ Erro ao carregar arquivo de plano: {str(e)}")
                return 1
        
        # Processar a feature
        logger.info(f"Iniciando processamento da feature com prompt: {args.prompt}")
        print(f"\n🚀 Iniciando criação da feature: '{args.prompt}'")
        print(f"⚙️  Modelo OpenAI: {args.model} (será usado no agente de conceito)")
        
        if execution_plan:
            print(f"📋 Usando plano de execução de: {args.plan_file}")
            result = agent.create_feature(args.prompt, execution_plan)
        else:
            print("📋 Gerando plano de execução automático...")
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