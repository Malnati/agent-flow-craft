import argparse
import logging
import os
import time
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
    parser.add_argument("--owner", type=str, help="Repository owner", default="your_repo_owner")
    parser.add_argument("--repo", type=str, help="Repository name", default="your_repo_name")
    args = parser.parse_args()
    
    if not args.token:
        logger.error("GitHub token não encontrado. Defina a variável de ambiente GITHUB_TOKEN ou use --token")
        return
    
    logger.info("Iniciando processo de criação de feature")
    logger.info(f"Prompt: {args.prompt}")
    
    # Pequeno timeout antes de executar os comandos
    time.sleep(1)
    
    try:
        agent = FeatureCreationAgent(args.token, args.owner, args.repo)
        logger.info("Executando feature creation agent")
        agent.execute_feature_creation(args.prompt, args.execution_plan)
        logger.info("Processo de criação de feature concluído com sucesso")
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")

if __name__ == "__main__":
    main()
