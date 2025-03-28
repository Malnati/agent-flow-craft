import argparse
import logging
import os
import yaml
from datetime import datetime
import sys
from pathlib import Path
import time
import json
import tempfile

from slugify import slugify
from src.core.core.logger import setup_logging, get_logger, log_execution

# Adicionar o diretório base ao path para permitir importações
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Project root
SRC_DIR = BASE_DIR / 'src'
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(BASE_DIR))

from src.apps.agent_manager.agents.feature_creation_agent import FeatureCreationAgent
from src.apps.agent_manager.agents.plan_validator import PlanValidator

@log_execution
def setup_logging_for_feature_agent():
    """Configuração específica de logs para o agente de feature"""
    logger = get_logger(__name__)
    logger.info("INÍCIO - setup_logging_for_feature_agent")
    
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file = f"feature_agent_{timestamp}.log"
        logger = setup_logging("feature_agent", log_file)
        logger.info("SUCESSO - Logger configurado")
        return logger
    except Exception as e:
        logger.error(f"FALHA - setup_logging_for_feature_agent | Erro: {str(e)}", exc_info=True)
        raise

# Configurar logging
logger = setup_logging_for_feature_agent()

@log_execution
def ensure_config_files():
    """Garante que os arquivos de configuração existam"""
    logger = get_logger(__name__)
    logger.info("INÍCIO - ensure_config_files")
    
    try:
        config_dir = "config"
        os.makedirs(config_dir, exist_ok=True)
        logger.debug(f"Diretório criado/verificado: {config_dir}")
        
        req_file = os.path.join(config_dir, "plan_requirements.yaml")
        if not os.path.exists(req_file):
            default_requirements = {
                "requisitos_entregaveis": [
                    {"nome": "Nome claro e específico", "obrigatorio": True},
                    {"descricao": "Descrição detalhada", "obrigatorio": True},
                    {"dependencias": "Lista de dependências necessárias", "obrigatorio": True},
                    {"exemplo_uso": "Exemplo prático de uso", "obrigatorio": True},
                    {"criterios_aceitacao": "Critérios mensuráveis", "obrigatorio": True},
                    {"resolucao_problemas": "Problemas e soluções", "obrigatorio": True},
                    {"passos_implementacao": "Passos detalhados", "obrigatorio": True}
                ]
            }
            
            with open(req_file, 'w', encoding='utf-8') as f:
                yaml.dump(default_requirements, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"SUCESSO - Arquivo de requisitos criado: {req_file}")
        else:
            logger.debug(f"Arquivo de requisitos já existe: {req_file}")
            
    except Exception as e:
        logger.error(f"FALHA - ensure_config_files | Erro: {str(e)}", exc_info=True)
        raise

@log_execution
def main():
    """Função principal do script"""
    logger = get_logger(__name__)
    logger.info("INÍCIO - main")
    
    try:
        ensure_config_files()
        
        parser = argparse.ArgumentParser(description="Execute the feature creation process.")
        parser.add_argument("prompt", type=str, help="The user prompt for feature creation.")
        parser.add_argument("execution_plan", type=str, help="The execution plan for the feature.")
        parser.add_argument("--target", required=True, type=str, 
                          help="Caminho completo para o repositório Git do projeto")
        parser.add_argument("--token", type=str, help="GitHub token", default=os.environ.get("GITHUB_TOKEN"))
        parser.add_argument("--owner", type=str, help="Repository owner (obrigatório).")
        parser.add_argument("--repo", type=str, help="Repository name (obrigatório).")
        parser.add_argument("--openai_token", type=str, help="Token da OpenAI", 
                            default=os.environ.get("OPENAI_API_KEY"))
        parser.add_argument("--max_attempts", type=int, help="Número máximo de tentativas", default=3)
        parser.add_argument("--config", type=str, help="Arquivo de configuração", 
                            default="config/plan_requirements.yaml")
        parser.add_argument("--verbose", action="store_true", help="Ativa modo verbose")
        
        args = parser.parse_args()
        
        if args.verbose:
            logger.setLevel(logging.DEBUG)
            logger.debug("Modo verbose ativado")
        
        # Verificar se o caminho do repositório é válido
        if not os.path.isdir(args.target):
            logger.error(f"FALHA - Diretório do repositório não encontrado: {args.target}")
            return
            
        git_dir = os.path.join(args.target, '.git')
        if not os.path.isdir(git_dir):
            logger.error(f"FALHA - O diretório não é um repositório Git: {args.target}")
            return
            
        # Mudar para o diretório do projeto
        os.chdir(args.target)
        logger.info(f"Trabalhando no diretório: {os.getcwd()}")
        
        if not args.token:
            logger.error("FALHA - Token GitHub ausente")
            return
            
        if not args.owner or not args.repo:
            logger.error("FALHA - Parâmetros owner/repo ausentes")
            return
        
        logger.info(f"Iniciando processo | Prompt: {args.prompt[:100]}...")
        
        agent = FeatureCreationAgent(args.token, args.owner, args.repo)
        validator = PlanValidator(logger)
        
        # Loop de auto-correção
        attempt = 0
        valid_plan = False
        current_plan = args.execution_plan
        
        while not valid_plan and attempt < args.max_attempts:
            attempt += 1
            logger.info(f"Tentativa {attempt} de {args.max_attempts}")
            
            # Validar plano
            validation_result = validator.validate(current_plan, args.openai_token)
            
            if validation_result.get("is_valid", False):
                valid_plan = True
                logger.info("Plano válido encontrado!")
            else:
                missing_items = validation_result.get("missing_items", [])
                logger.warning(f"Plano inválido. Itens ausentes: {missing_items}")
                
                # Solicitar correção
                try:
                    corrected_plan = request_plan_correction(
                        args.prompt, 
                        current_plan, 
                        validation_result, 
                        args.openai_token,
                        args.config
                    )
                    current_plan = corrected_plan
                    logger.info("Plano corrigido recebido")
                except Exception as e:
                    logger.error(f"Erro ao corrigir plano: {str(e)}")
                    break
        
        # Executar com o plano final
        if valid_plan:
            logger.info("Executando com plano validado")
        else:
            logger.warning(f"Execução com plano parcial após {args.max_attempts} tentativas")
        
        # Executar a criação da feature
        agent.execute_feature_creation(args.prompt, current_plan, openai_token=args.openai_token)
        logger.info("Processo de criação de feature concluído")
        
    except Exception as e:
        logger.error(f"FALHA - main | Erro: {str(e)}", exc_info=True)
        raise

@log_execution
def request_plan_correction(prompt, current_plan, validation_result, openai_token, config_file):
    """Solicita correção do plano usando a API da OpenAI e os requisitos do arquivo YAML"""
    from openai import OpenAI
    
    # Carregar requisitos do arquivo YAML
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            requirements = yaml.safe_load(f)
    except Exception:
        requirements = {}
    
    # Extrair detalhes dos requisitos para o prompt
    req_details = ""
    if "requisitos_entregaveis" in requirements:
        req_details = "Cada entregável deve incluir:\n"
        for req in requirements["requisitos_entregaveis"]:
            for key, desc in req.items():
                if key != "obrigatorio":
                    req_details += f"- {key}: {desc}\n"
    else:
        req_details = (
            "Cada entregável deve incluir: nome, descrição, dependências, "
            "exemplo de uso, critérios de aceitação, resolução de problemas "
            "e passos de implementação."
        )
    
    # Extrair itens ausentes
    missing_items = validation_result.get("missing_items", [])
    missing_items_text = "\n".join([f"- {item}" for item in missing_items])
    
    # Detalhes por entregável
    details_text = ""
    if "detalhes_por_entregavel" in validation_result:
        for entregavel in validation_result["detalhes_por_entregavel"]:
            nome = entregavel.get("nome", "Entregável sem nome")
            itens = entregavel.get("itens_ausentes", [])
            if itens:
                details_text += f"\n### Para o entregável '{nome}':\n"
                details_text += "\n".join([f"- Falta: {item}" for item in itens])
    
    # Criar mensagem de correção
    correction_message = (
        f"# Solicitação de Correção de Plano\n\n"
        f"## Prompt original:\n{prompt}\n\n"
        f"## Plano atual com problemas:\n{current_plan}\n\n"
        f"## Itens ausentes no plano:\n{missing_items_text}\n"
        f"{details_text}\n\n"
        f"## Requisitos para entregáveis:\n{req_details}\n\n"
        f"## Instruções:\n"
        f"Por favor, corrija o plano acima incluindo todos os itens ausentes. "
        f"Forneça o plano completo corrigido, não apenas os itens ausentes."
    )
    
    # Chamar API para correção
    client = OpenAI(api_key=openai_token)
    
    response = client.chat.completions.create(
        model="gpt-4",  # Modelo mais avançado para correção
        messages=[
            {"role": "system", "content": "Você é um especialista em criar planos de execução de software."},
            {"role": "user", "content": correction_message}
        ],
        temperature=0.7,
        max_tokens=4000
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Processo interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Erro fatal durante execução: {str(e)}", exc_info=True)
        sys.exit(1)
