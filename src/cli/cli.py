import argparse
import sys
from pathlib import Path

# Adicionar o diretório base ao path para permitir importações
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR.parent))  # Adiciona o diretório pai de src

try:
    from src.scripts import (
        run_agent_feature_coordinator,
        run_agent_github_integration,
        run_agent_python_refactor,
        util_generate_docs_index,
        util_clean_pycache,
    )
except ImportError:
    # Fallback para importação direta quando instalado como pacote
    from src.scripts import (
        run_agent_feature_coordinator,
        run_agent_github_integration,
        run_agent_python_refactor,
        util_generate_docs_index,
        util_clean_pycache,
    )


def main():
    parser = argparse.ArgumentParser(
        prog="agent-flow-craft",
        description="Automatização de agentes para fluxo de desenvolvimento orientado a microtarefas.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcomando: feature
    feature_parser = subparsers.add_parser("feature", help="Cria uma nova feature a partir de um prompt")
    feature_parser.add_argument("prompt", help="Descrição da feature a ser criada")
    feature_parser.add_argument("--plan_file", help="Arquivo JSON contendo o plano de execução (opcional)")
    feature_parser.add_argument("--project_dir", dest="target", help="Diretório do projeto onde a feature será criada")
    feature_parser.add_argument("--output", help="Arquivo de saída para o resultado")
    feature_parser.add_argument("--context_dir", help="Diretório para armazenar arquivos de contexto")
    feature_parser.add_argument("--github_token", help="Token de acesso ao GitHub")
    feature_parser.add_argument("--owner", help="Proprietário do repositório GitHub")
    feature_parser.add_argument("--repo", help="Nome do repositório GitHub")
    feature_parser.add_argument("--openai_token", help="Token de acesso à OpenAI")
    feature_parser.add_argument("--model", help="Modelo da OpenAI a ser utilizado")
    feature_parser.add_argument("--elevation_model", help="Modelo alternativo para elevação em caso de falha")
    feature_parser.add_argument("--force", action="store_true", help="Força o uso direto do modelo de elevação")

    # Subcomando: github
    github_parser = subparsers.add_parser("github", help="Processa um conceito de feature para criar issue, branch e PR no GitHub")
    github_parser.add_argument("context_id", help="ID do contexto a ser processado")
    github_parser.add_argument("--github_token", help="Token de acesso ao GitHub")
    github_parser.add_argument("--owner", help="Proprietário do repositório GitHub")
    github_parser.add_argument("--repo", help="Nome do repositório GitHub")
    github_parser.add_argument("--project_dir", dest="target", help="Diretório do projeto onde o conceito será aplicado")
    github_parser.add_argument("--output", help="Arquivo de saída para o resultado")
    github_parser.add_argument("--context_dir", help="Diretório para armazenar/acessar arquivos de contexto")
    github_parser.add_argument("--base_branch", help="Nome da branch base para criar a nova branch")

    # Subcomando: refactor
    refactor_parser = subparsers.add_parser("refactor", help="Executa o agente de refatoração")
    refactor_parser.add_argument("--project_dir", required=True, help="Diretório do projeto")
    refactor_parser.add_argument("--scope", help="Arquivo ou diretório alvo")
    refactor_parser.add_argument("--level", choices=["leve", "moderado", "agressivo"], help="Nível de refatoração")
    refactor_parser.add_argument("--dry_run", action="store_true", help="Simula as mudanças sem aplicar")
    refactor_parser.add_argument("--force", action="store_true", help="Força execução")
    refactor_parser.add_argument("--output", help="Arquivo de saída")

    # Subcomando: docs
    docs_parser = subparsers.add_parser("docs", help="Gera o índice da documentação")
    docs_parser.add_argument("--output", help="Diretório de saída para a documentação")

    # Subcomando: clean
    clean_parser = subparsers.add_parser("clean", help="Limpa arquivos de cache Python")
    clean_parser.add_argument("--target", help="Diretório alvo para limpeza")
    clean_parser.add_argument("--recursive", action="store_true", help="Limpa recursivamente")

    args = parser.parse_args()

    try:
        if args.command == "feature":
            # Converter argumentos para o formato esperado pelo script
            sys.argv = [sys.argv[0]] + ([args.prompt] if hasattr(args, 'prompt') else [])
            for arg_name, arg_value in vars(args).items():
                if arg_name != 'command' and arg_name != 'prompt' and arg_value is not None:
                    if isinstance(arg_value, bool):
                        if arg_value:
                            sys.argv.append(f"--{arg_name}")
                    else:
                        sys.argv.append(f"--{arg_name}")
                        sys.argv.append(str(arg_value))
            sys.exit(run_agent_feature_coordinator.main())
        elif args.command == "github":
            # Converter argumentos para o formato esperado pelo script
            sys.argv = [sys.argv[0]] + ([args.context_id] if hasattr(args, 'context_id') else [])
            for arg_name, arg_value in vars(args).items():
                if arg_name != 'command' and arg_name != 'context_id' and arg_value is not None:
                    if isinstance(arg_value, bool):
                        if arg_value:
                            sys.argv.append(f"--{arg_name}")
                    else:
                        sys.argv.append(f"--{arg_name}")
                        sys.argv.append(str(arg_value))
            sys.exit(run_agent_github_integration.main())
        elif args.command == "refactor":
            sys.exit(run_agent_python_refactor.main(args))
        elif args.command == "docs":
            sys.exit(util_generate_docs_index.main(args))
        elif args.command == "clean":
            sys.exit(util_clean_pycache.main(args))
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())