# Executar o guardrail
logger.info("Executando TDDGuardrailAgent...")

# Configurar o diretório de contexto do agente
guardrail_agent.context_dir = Path(args.context_dir)
logger.info(f"Diretório de contexto configurado: {args.context_dir}")

result = guardrail_agent.execute_tdd_guardrail(
    criteria_id=args.criteria_id,
    concept_id=args.concept_id,
    project_dir=args.project_dir
)

# Verificar o resultado 