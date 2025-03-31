import asyncio
import os
from core.apps.agent_manager.agents.feature_creation_agent import FeatureCreationAgent

async def criar_nova_feature(prompt_text):
    # Configurar tokens
    github_token = os.getenv("GITHUB_TOKEN")
    openai_token = os.getenv("OPENAI_API_KEY")
    
    if not github_token or not openai_token:
        raise ValueError("GITHUB_TOKEN e OPENAI_API_KEY são necessários")
    
    # Inicializar agente
    agent = FeatureCreationAgent(
        github_token=github_token,
        repo_owner="seu_usuario_github",  # Altere para seu usuário
        repo_name="seu_repositorio"       # Altere para seu repositório
    )
    
    try:
        # Inicializar agentes locais
        agent.initialize_local_agents()
        
        # Criar plano de execução inicial
        execution_plan = {
            "steps": [
                "1. Análise inicial do código",
                "2. Implementação da feature",
                "3. Testes unitários",
                "4. Documentação"
            ]
        }
        
        # Executar criação da feature
        issue_number, branch_name = await agent.execute_feature_creation(
            prompt_text=prompt_text,
            execution_plan=execution_plan,
            openai_token=openai_token
        )
        
        print(f"\nFeature criada com sucesso!")
        print(f"Issue: #{issue_number}")
        print(f"Branch: {branch_name}")
        
    finally:
        # Cleanup
        if hasattr(agent, 'local_agents'):
            for local_agent in agent.local_agents.values():
                await local_agent.stop()

if __name__ == "__main__":
    # Exemplo de uso
    prompt = """
    Implementar sistema de autenticação MCP
    
    Requisitos:
    - Integração com OAuth2
    - Suporte a múltiplos providers
    - Sistema de cache de tokens
    - Renovação automática de credenciais
    """
    
    asyncio.run(criar_nova_feature(prompt)) 