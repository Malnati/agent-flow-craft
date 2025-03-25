import argparse
from agents.feature_creation_agent import FeatureCreationAgent

def main():
    parser = argparse.ArgumentParser(description="Execute the feature creation process.")
    parser.add_argument("prompt", type=str, help="The user prompt for feature creation.")
    parser.add_argument("execution_plan", type=str, help="The execution plan for the feature.")
    args = parser.parse_args()

    github_token = "your_github_token"
    repo_owner = "your_repo_owner"
    repo_name = "your_repo_name"

    agent = FeatureCreationAgent(github_token, repo_owner, repo_name)
    agent.execute_feature_creation(args.prompt, args.execution_plan)

if __name__ == "__main__":
    main()
