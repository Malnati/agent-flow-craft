# Criando Features com MCP no Cursor

## Como Usar

1. Abra o Command Palette (Ctrl+Shift+P ou Cmd+Shift+P)
2. Digite "MCP: Create Feature"
3. Cole o prompt da sua feature

## Exemplo de Prompt

```markdown
Implementar sistema de autenticação MCP

Requisitos:
- Integração com OAuth2
- Suporte a múltiplos providers
- Sistema de cache de tokens
- Renovação automática de credenciais

Detalhes Técnicos:
- Usar FastAPI para endpoints
- Implementar JWT
- Adicionar rate limiting
- Documentar com OpenAPI
```

## Estrutura do Projeto

O MCP irá:
1. Criar uma nova issue no GitHub
2. Gerar uma branch com o nome apropriado
3. Criar um plano de execução
4. Inicializar o PR

## Logs e Monitoramento

Os logs podem ser visualizados:
- No terminal integrado do Cursor
- No painel de output (View -> Output)
- No arquivo `.cursor/logs/mcp.log` 