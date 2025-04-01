import argparse
from agent_platform.scripts import (
    run_plan_validator,
    run_context_manager,
    start_refactor_agent,
    run_tdd_criteria_agent,
    run_tdd_guardrail_agent,
    test_mcp_e2e,
    install_cursor,
    pack_project,
)

def main():
    parser = argparse.ArgumentParser(
        prog="agent-flow-craft",
        description="Automatização de agentes para fluxo de desenvolvimento orientado a microtarefas.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcomando: run
    run_parser = subparsers.add_parser("run", help="Executa o validador de planos")
    run_parser.add_argument("--plan", required=True, help="Arquivo JSON do plano")
    run_parser.add_argument("--output", help="Arquivo de saída")
    run_parser.add_argument("--requirements", help="Arquivo de requisitos")
    run_parser.add_argument("--context_dir", help="Diretório dos contextos")
    run_parser.add_argument("--project_dir", help="Diretório do projeto")
    run_parser.add_argument("--model", help="Modelo OpenAI")

    # Subcomando: context
    context_parser = subparsers.add_parser("context", help="Gerencia contextos")
    context_parser.add_argument("operation", choices=["lista", "obter", "criar", "atualizar", "excluir", "limpar"], help="Operação a executar")
    context_parser.add_argument("--context_id", help="ID do contexto")
    context_parser.add_argument("--data_file", help="Arquivo JSON com os dados")
    context_parser.add_argument("--type", help="Tipo de contexto")
    context_parser.add_argument("--limit", type=int, help="Limite de resultados")
    context_parser.add_argument("--days", type=int, help="Limite de dias")
    context_parser.add_argument("--output", help="Arquivo de saída")
    context_parser.add_argument("--merge", action="store_true", help="Usar merge na atualização")
    context_parser.add_argument("--context_dir", help="Diretório do contexto")

    # Subcomando: refactor
    refactor_parser = subparsers.add_parser("refactor", help="Executa o agente de refatoração")
    refactor_parser.add_argument("--project_dir", required=True, help="Diretório do projeto")
    refactor_parser.add_argument("--scope", help="Arquivo ou diretório alvo")
    refactor_parser.add_argument("--level", choices=["leve", "moderado", "agressivo"], help="Nível de refatoração")
    refactor_parser.add_argument("--dry_run", action="store_true", help="Simula as mudanças sem aplicar")
    refactor_parser.add_argument("--force", action="store_true", help="Força execução")
    refactor_parser.add_argument("--output", help="Arquivo de saída")

    # Subcomando: tdd-criteria
    tdd_criteria_parser = subparsers.add_parser("tdd-criteria", help="Executa o agente de critérios TDD")
    tdd_criteria_parser.add_argument("--context_id", help="ID do contexto")
    tdd_criteria_parser.add_argument("--project_dir", help="Diretório do projeto")
    tdd_criteria_parser.add_argument("--output", help="Arquivo de saída")
    tdd_criteria_parser.add_argument("--context_dir", help="Diretório do contexto")
    tdd_criteria_parser.add_argument("--openai_token", help="Token OpenAI")
    tdd_criteria_parser.add_argument("--model", help="Modelo OpenAI")
    tdd_criteria_parser.add_argument("--elevation_model", help="Modelo de elevação")
    tdd_criteria_parser.add_argument("--force", action="store_true", help="Força execução")

    # Subcomando: tdd-guardrail
    tdd_guardrail_parser = subparsers.add_parser("tdd-guardrail", help="Executa o agente de guardrails TDD")
    tdd_guardrail_parser.add_argument("--criteria_id", help="ID do critério")
    tdd_guardrail_parser.add_argument("--concept_id", help="ID do conceito")
    tdd_guardrail_parser.add_argument("--project_dir", help="Diretório do projeto")
    tdd_guardrail_parser.add_argument("--output", help="Arquivo de saída")
    tdd_guardrail_parser.add_argument("--context_dir", help="Diretório do contexto")
    tdd_guardrail_parser.add_argument("--openai_token", help="Token OpenAI")
    tdd_guardrail_parser.add_argument("--model", help="Modelo OpenAI")
    tdd_guardrail_parser.add_argument("--elevation_model", help="Modelo de elevação")
    tdd_guardrail_parser.add_argument("--force", action="store_true", help="Força execução")

    # Subcomando: test-mcp
    subparsers.add_parser("test-mcp", help="Executa o teste MCP")

    # Subcomando: install-cursor
    subparsers.add_parser("install-cursor", help="Instala o cursor")

    # Subcomando: pack
    pack_parser = subparsers.add_parser("pack", help="Empacota o projeto")
    pack_parser.add_argument("--out", required=True, help="Arquivo de saída do empacotamento")

    args = parser.parse_args()

    if args.command == "run":
        run_plan_validator.main(args)
    elif args.command == "context":
        run_context_manager.main(args)
    elif args.command == "refactor":
        start_refactor_agent.main(args)
    elif args.command == "tdd-criteria":
        run_tdd_criteria_agent.main(args)
    elif args.command == "tdd-guardrail":
        run_tdd_guardrail_agent.main(args)
    elif args.command == "test-mcp":
        test_mcp_e2e.main()
    elif args.command == "install-cursor":
        install_cursor.main()
    elif args.command == "pack":
        pack_project.main(args)

if __name__ == "__main__":
    main()