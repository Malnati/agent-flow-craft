#!/usr/bin/env python3
"""
Script para executar o ConceptGenerationAgent diretamente.
Gera conceitos de features a partir de prompts do usuário usando a OpenAI.
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

# Importar o agente de conceito
from apps.agent_manager.agents import ConceptGenerationAgent

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
        description="Executa o ConceptGenerationAgent para gerar conceitos de features",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "prompt",
        help="Descrição da feature a ser conceituada (texto ou caminho para arquivo .txt)"
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
        "--git_log_file",
        help="Arquivo com log do Git para contexto (opcional)"
    )
    
    parser.add_argument(
        "--output",
        help="Arquivo de saída para o conceito gerado (opcional)"
    )
    
    parser.add_argument(
        "--context_dir",
        default="agent_context",
        help="Diretório para armazenar/acessar arquivos de contexto (padrão: agent_context)"
    )
    
    parser.add_argument(
        "--project_dir",
        help="Diretório do projeto onde o conceito será aplicado (opcional)"
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
        
        # Verificar prompt - pode ser texto diretamente ou arquivo
        prompt_text = args.prompt
        if os.path.isfile(prompt_text):
            with open(prompt_text, 'r', encoding='utf-8') as f:
                prompt_text = f.read().strip()
            logger.info(f"Prompt carregado do arquivo: {args.prompt}")
        
        # Verificar log do Git - pode ser arquivo ou None
        git_log = None
        if args.git_log_file and os.path.isfile(args.git_log_file):
            with open(args.git_log_file, 'r', encoding='utf-8') as f:
                git_log = f.read().strip()
            logger.info(f"Log do Git carregado do arquivo: {args.git_log_file}")
        
        # Inicializar agente de conceito
        openai_token = args.openai_token or os.environ.get('OPENAI_API_KEY', '')
        if not openai_token:
            logger.warning("Token OpenAI não fornecido. Algumas funcionalidades podem estar limitadas.")
        
        # Criar diretório de contexto se não existir
        context_dir = Path(args.context_dir)
        if not context_dir.exists():
            context_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Diretório de contexto criado: {context_dir}")
        
        # Configurar diretório de contexto
        logger.info(f"Criando diretório de contexto: {context_dir} (absoluto: {context_dir.resolve()})")
        
        # Inicializar o agente com o diretório de contexto personalizado
        agent = ConceptGenerationAgent(openai_token=openai_token, model=args.model)
        # Definir diretório de contexto explicitamente
        agent.context_dir = context_dir
        logger.info(f"Diretório de contexto do agente configurado: {agent.context_dir}")
        logger.info(f"Modelo OpenAI configurado: {args.model}")
        
        # Verificar diretório do projeto se fornecido
        if args.project_dir:
            project_dir = Path(args.project_dir)
            if not project_dir.exists():
                logger.warning(f"Diretório de projeto não encontrado: {project_dir}")
            else:
                logger.info(f"Utilizando diretório de projeto: {project_dir}")
                # Se necessário, pode-se adicionar lógica específica ao diretório do projeto aqui
                
        # Gerar conceito
        logger.info("Gerando conceito com base no prompt...")
        concept = agent.generate_concept(prompt_text, git_log)
        
        # Verificar se o contexto foi salvo
        logger.info(f"Verificando arquivos no diretório de contexto: {context_dir}")
        if context_dir.exists():
            files = list(context_dir.glob("*.json"))
            logger.info(f"Arquivos encontrados: {files}")
            if not files:
                logger.warning(f"Nenhum arquivo de contexto encontrado em {context_dir}")
                
                # Tentar salvar manualmente
                logger.info("Tentando salvar contexto manualmente...")
                context_id = agent._save_concept_to_context(concept, prompt_text)
                logger.info(f"Contexto salvo manualmente com ID: {context_id}")
        else:
            logger.error(f"Diretório de contexto não existe: {context_dir}")
        
        # Exibir conceito
        print("\n🧠 Conceito gerado:\n")
        print(json.dumps(concept, indent=2, ensure_ascii=False))
        
        # Salvar conceito se solicitado
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(concept, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Conceito salvo em: {args.output}")
        
        # Retorno bem-sucedido
        return 0
        
    except KeyboardInterrupt:
        logger.warning("Processo interrompido pelo usuário")
        print("\n⚠️  Processo interrompido pelo usuário")
        return 130
        
    except Exception as e:
        logger.error(f"Erro ao gerar conceito: {str(e)}", exc_info=True)
        print(f"\n❌ Erro: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 