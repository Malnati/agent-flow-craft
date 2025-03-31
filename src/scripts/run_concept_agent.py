#!/usr/bin/env python3
"""
Script para executar o agente de geração de conceitos.

Este script configura e executa o ConceptGenerationAgent, responsável por
gerar conceitos iniciais de features a partir de um prompt.
"""
import os
import sys
import json
import argparse
import time
from pathlib import Path

# Adicionar o diretório raiz ao path para permitir importações
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Importar componentes do AgentFlowCraft
from core.core.logger import setup_logging, get_logger, log_execution
from apps.agent_manager.agents import ConceptGenerationAgent

# Configurar logger
logger = get_logger(__name__)

@log_execution
def setup_logging_for_concept_agent():
    """Configuração específica de logs para o agente de conceito"""
    logger = get_logger(__name__)
    logger.info("INÍCIO - setup_logging_for_concept_agent")
    
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file = f"concept_agent_{timestamp}.log"
        logger = setup_logging("concept_agent", log_file)
        logger.info("SUCESSO - Logger configurado")
        return logger
    except Exception as e:
        logger.error(f"FALHA - setup_logging_for_concept_agent | Erro: {str(e)}", exc_info=True)
        raise

@log_execution
def parse_arguments():
    """
    Analisa os argumentos da linha de comando.
    
    Returns:
        argparse.Namespace: Argumentos da linha de comando
    """
    parser = argparse.ArgumentParser(
        description="Executa o agente de geração de conceitos",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "prompt",
        help="Descrição da feature para geração do conceito (texto ou caminho para arquivo .txt)"
    )
    
    parser.add_argument(
        "--output",
        help="Arquivo de saída para o resultado (opcional)"
    )
    
    parser.add_argument(
        "--git_log_file",
        help="Arquivo contendo log do Git para contexto (opcional)"
    )
    
    parser.add_argument(
        "--context_dir",
        default="agent_context",
        help="Diretório para armazenar contextos (padrão: agent_context)"
    )
    
    parser.add_argument(
        "--project_dir",
        help="Diretório do projeto (opcional, usa diretório atual se não especificado)"
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
        default="gpt-4-turbo",
        help="Modelo da OpenAI para elevação em caso de falha (padrão: gpt-4-turbo)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forçar uso do modelo de elevação diretamente"
    )
    
    # Argumento para modo MCP
    parser.add_argument(
        "--mcp",
        action="store_true",
        help="Executar no modo MCP (stdin/stdout)"
    )
    
    return parser.parse_args()

def handle_mcp_command(payload):
    """
    Manipula a execução quando chamado via MCP.
    
    Args:
        payload (dict): Parâmetros fornecidos via MCP
        
    Returns:
        dict: Resultado da operação
    """
    logger.info("Executando via MCP com payload")
    
    try:
        # Extrair parâmetros
        prompt = payload.get("prompt")
        if not prompt:
            return {"status": "error", "error": "Prompt é obrigatório"}
            
        openai_token = payload.get("openai_token", os.environ.get("OPENAI_API_KEY", ""))
        project_dir = payload.get("project_dir", os.getcwd())
        context_dir = payload.get("context_dir", "agent_context")
        model = payload.get("model", "gpt-4-turbo")
        elevation_model = payload.get("elevation_model", "gpt-4-turbo")
        force = payload.get("force", False)
        git_log_file = payload.get("git_log_file")
        
        # Verificar prompt - pode ser texto diretamente ou arquivo
        if os.path.isfile(prompt):
            with open(prompt, 'r', encoding='utf-8') as f:
                prompt_text = f.read().strip()
            logger.info(f"Prompt carregado do arquivo: {prompt}")
        else:
            prompt_text = prompt
        
        # Verificar e criar diretório de contexto se necessário
        Path(context_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"Diretório de contexto: {context_dir}")
        
        # Inicializar agente
        agent = ConceptGenerationAgent(openai_token=openai_token)
        
        # Configurar modelos
        if hasattr(agent, 'set_model'):
            agent.set_model(model)
            logger.info(f"Modelo configurado: {model}")
            
        if hasattr(agent, 'set_elevation_model'):
            agent.set_elevation_model(elevation_model)
            logger.info(f"Modelo de elevação configurado: {elevation_model}")
        
        if hasattr(agent, 'set_force_elevation') and force:
            agent.set_force_elevation(True)
            logger.info("Força de elevação ativada")
        
        # Executar geração de conceito
        logger.info(f"Gerando conceito para prompt: {prompt_text[:100]}...")
        git_log = None
        if git_log_file:
            if os.path.exists(git_log_file):
                with open(git_log_file, 'r', encoding='utf-8') as f:
                    git_log = f.read()
                logger.info(f"Log Git carregado de: {git_log_file}")
        
        concept = agent.generate_concept(
            prompt=prompt_text,
            project_dir=project_dir,
            context_dir=context_dir,
            git_log=git_log
        )
        
        logger.info(f"Conceito gerado com ID: {concept.get('context_id', 'DESCONHECIDO')}")
        return {
            "status": "success",
            "result": concept
        }
        
    except Exception as e:
        logger.error(f"Erro ao executar via MCP: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }

@log_execution
def main():
    """
    Função principal de execução do script.
    """
    # Configurar logging específico
    logger = setup_logging_for_concept_agent()
    
    # Verificar modo de execução
    if len(sys.argv) > 1 and sys.argv[1] == "--mcp":
        # Modo MCP: processar comandos via stdin/stdout
        logger.info("Iniciando no modo MCP...")
        
        try:
            # Processar comandos do stdin
            for line in sys.stdin:
                if not line.strip():
                    continue
                    
                logger.info("Comando MCP recebido")
                
                try:
                    # Ler comando JSON
                    command = json.loads(line)
                    payload = command.get("payload", {})
                    message_id = command.get("message_id", "unknown")
                    
                    # Processar comando
                    result = handle_mcp_command(payload)
                    result["message_id"] = message_id
                    
                    # Enviar resposta
                    print(json.dumps(result), flush=True)
                    logger.info(f"Resposta MCP enviada para message_id: {message_id}")
                    
                except Exception as e:
                    # Erro no processamento
                    error_response = {
                        "message_id": command.get("message_id", "unknown") if 'command' in locals() else "unknown",
                        "status": "error",
                        "error": str(e)
                    }
                    print(json.dumps(error_response), flush=True)
                    logger.error(f"Erro processando comando MCP: {str(e)}", exc_info=True)
        
        except Exception as e:
            logger.error(f"Erro fatal no modo MCP: {str(e)}", exc_info=True)
            return 1
            
    else:
        # Modo normal: processar argumentos da linha de comando
        try:
            # Analisar argumentos
            args = parse_arguments()
            
            # Verificar se é modo MCP via argumento
            if args.mcp:
                # Reexecutar no modo MCP
                os.execv(sys.executable, [sys.executable, __file__, "--mcp"])
                return 0
            
            # Verificar prompt - pode ser texto diretamente ou arquivo
            prompt_text = args.prompt
            if os.path.isfile(prompt_text):
                with open(prompt_text, 'r', encoding='utf-8') as f:
                    prompt_text = f.read().strip()
                logger.info(f"Prompt carregado do arquivo: {args.prompt}")
            
            # Verificar e criar diretório de contexto se necessário
            context_dir = Path(args.context_dir)
            if not context_dir.exists():
                context_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Diretório de contexto criado: {context_dir}")
            
            # Verificar diretório do projeto
            project_dir = args.project_dir or os.getcwd()
            logger.info(f"Diretório do projeto: {project_dir}")
            
            # Obter token OpenAI
            openai_token = args.openai_token or os.environ.get("OPENAI_API_KEY", "")
            if not openai_token:
                logger.warning("Token OpenAI não fornecido")
                print("\n⚠️  Aviso: Token OpenAI não fornecido. As operações podem falhar.")
            
            # Inicializar agente
            agent = ConceptGenerationAgent(openai_token=openai_token)
            
            # Configurar modelos
            if hasattr(agent, 'set_model'):
                agent.set_model(args.model)
                logger.info(f"Modelo configurado: {args.model}")
                
            if hasattr(agent, 'set_elevation_model'):
                agent.set_elevation_model(args.elevation_model)
                logger.info(f"Modelo de elevação configurado: {args.elevation_model}")
            
            if hasattr(agent, 'set_force_elevation') and args.force:
                agent.set_force_elevation(True)
                logger.info("Força de elevação ativada")
            
            # Obter log Git se especificado
            git_log = None
            if args.git_log_file:
                if os.path.exists(args.git_log_file):
                    with open(args.git_log_file, 'r', encoding='utf-8') as f:
                        git_log = f.read()
                    logger.info(f"Log Git carregado de: {args.git_log_file}")
                else:
                    logger.warning(f"Arquivo de log Git não encontrado: {args.git_log_file}")
            
            # Executar geração de conceito
            print(f"\n🚀 Gerando conceito para: '{prompt_text[:100]}...'")
            print(f"🔄 Usando modelo: {args.model}")
            if args.force:
                print(f"⚠️  Força de elevação ativada: usando diretamente {args.elevation_model}")
            
            concept = agent.generate_concept(
                prompt=prompt_text,
                project_dir=project_dir,
                context_dir=str(context_dir),
                git_log=git_log
            )
            
            # Exibir resultado
            print("\n✅ Conceito gerado com sucesso!")
            print(f"📋 ID de Contexto: {concept.get('context_id')}")
            print(f"📌 Título: {concept.get('summary', 'N/A')}")
            
            # Salvar resultado se solicitado
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(concept, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Resultado salvo em: {args.output}")
            
            logger.info(f"Conceito gerado com sucesso: {concept.get('context_id')}")
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