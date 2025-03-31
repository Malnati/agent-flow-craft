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

# Adicionar o diretório base ao path para permitir importações
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR.parent))  # Adiciona o diretório pai de src

from src.core.core.logger import get_logger, log_execution
from src.core.core.utils import TokenValidator

# Importar o agente coordenador
from src.apps.agent_manager.agents import FeatureCoordinatorAgent
from src.apps.agent_manager.agents.context_manager import ContextManager

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
        "--owner",
        help="Proprietário do repositório GitHub (opcional, usa variável de ambiente GITHUB_OWNER se não especificado)"
    )
    
    parser.add_argument(
        "--repo",
        help="Nome do repositório GitHub (opcional, usa variável de ambiente GITHUB_REPO se não especificado)"
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
        "--elevation_model",
        help="Modelo alternativo para elevação em caso de falha (opcional)"
    )
    
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Força o uso direto do modelo de elevação, ignorando o modelo padrão"
    )
    
    return parser.parse_args()

def main():
    """
    Função principal que coordena a execução.
    
    Returns:
        int: Código de saída (0 para sucesso, 1 para erro)
    """
    try:
        # Obter argumentos da linha de comando
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
        
        # Validar tokens obrigatórios
        try:
            TokenValidator.validate_openai_token(openai_token, required=True)
            TokenValidator.validate_github_token(github_token, required=True)
            logger.info("Todos os tokens validados com sucesso")
        except ValueError as e:
            logger.error(f"Tokens obrigatórios inválidos: {str(e)}")
            print(f"\n❌ Erro: Tokens obrigatórios inválidos: {str(e)}")
            print("\nPara executar o agente, você precisa definir as seguintes variáveis de ambiente:")
            print("  OPENAI_API_KEY - Token da API da OpenAI")
            print("  GITHUB_TOKEN - Token do GitHub com permissões para criar issues e branches")
            print("\nExemplo:")
            print("  export OPENAI_API_KEY='sk-....'")
            print("  export GITHUB_TOKEN='ghp_....'")
            return 1
        
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
        
        # Se fornecidos, substituir os valores padrão
        if args.owner:
            agent.repo_owner = args.owner
        if args.repo:
            agent.repo_name = args.repo
        
        # Configurar o diretório de contexto do agente
        if hasattr(agent, 'context_dir'):
            agent.context_dir = context_dir
        elif hasattr(agent, 'set_context_dir'):
            agent.set_context_dir(str(context_dir))
            
        # Configurar o modelo, se possível
        if hasattr(agent, 'concept_agent') and hasattr(agent.concept_agent, 'set_model'):
            agent.concept_agent.set_model(args.model)
            logger.info(f"Modelo configurado para ConceptAgent: {args.model}")
            
        # Configurar o modelo de elevação, se fornecido
        if args.elevation_model:
            if hasattr(agent, 'concept_agent') and hasattr(agent.concept_agent, 'set_elevation_model'):
                agent.concept_agent.set_elevation_model(args.elevation_model)
                logger.info(f"Modelo de elevação configurado para ConceptAgent: {args.elevation_model}")
            
            # Configurar elevation model para outros agentes usados internamente
            for agent_attr in ['feature_concept_agent', 'tdd_criteria_agent', 'github_agent']:
                if hasattr(agent, agent_attr) and hasattr(getattr(agent, agent_attr), 'set_elevation_model'):
                    getattr(agent, agent_attr).set_elevation_model(args.elevation_model)
                    logger.info(f"Modelo de elevação configurado para {agent_attr}: {args.elevation_model}")
        
        # Configurar o modo force, se ativado
        if args.force:
            logger.info("Modo force ativado: usando diretamente o modelo de elevação")
            
            # Aplicar force em todos os agentes internos que suportam
            for agent_attr in ['concept_agent', 'feature_concept_agent', 'tdd_criteria_agent', 'github_agent']:
                if hasattr(agent, agent_attr):
                    agent_instance = getattr(agent, agent_attr)
                    if hasattr(agent_instance, 'force'):
                        agent_instance.force = True
                        logger.info(f"Modo force configurado para {agent_attr}")
                    
                    # Se temos modelo de elevação, usar diretamente como modelo principal
                    if args.elevation_model and hasattr(agent_instance, 'set_model') and hasattr(agent_instance, 'model'):
                        agent_instance.set_model(args.elevation_model)
                        logger.info(f"Substituído modelo principal de {agent_attr} para {args.elevation_model} devido ao modo force")
        
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
        
        if args.elevation_model:
            print(f"🔄 Modelo de elevação: {args.elevation_model}")
            if args.force:
                print(f"⚡ Modo force ativado: usando diretamente o modelo de elevação")
        
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