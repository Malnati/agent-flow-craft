import argparse
import logging
import os
from datetime import datetime
from agents.feature_creation_agent import FeatureCreationAgent

def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"feature_agent_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("feature_agent")

def main():
    logger = setup_logging()
    
    parser = argparse.ArgumentParser(description="Execute the feature creation process.")
    parser.add_argument("prompt", type=str, help="The user prompt for feature creation.")
    parser.add_argument("execution_plan", type=str, help="The execution plan for the feature.")
    parser.add_argument("--token", type=str, help="GitHub token", default=os.environ.get("GITHUB_TOKEN"))
    parser.add_argument("--owner", type=str, help="Repository owner (obrigatório).")
    parser.add_argument("--repo", type=str, help="Repository name (obrigatório).")
    parser.add_argument("--openai_token", type=str, help="Token da OpenAI para notificação opcional.")
    args = parser.parse_args()
    
    if not args.token:
        logger.error("GitHub token não encontrado. Defina a variável de ambiente GITHUB_TOKEN ou use --token")
        return

    if not args.owner or not args.repo:
        logger.error("O argumento --owner e --repo são obrigatórios. Sugestão: use 'git config --get remote.origin.url' para verificar seu repositório.")
        return
    
    logger.info("Iniciando processo de criação de feature")
    logger.info(f"Prompt: {args.prompt}")
    
    try:
        agent = FeatureCreationAgent(args.token, args.owner, args.repo)
        logger.info("Executando feature creation agent")
        agent.execute_feature_creation(args.prompt, args.execution_plan, openai_token=args.openai_token)
        logger.info("Processo de criação de feature concluído com sucesso")
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")

if __name__ == "__main__":
    main()
