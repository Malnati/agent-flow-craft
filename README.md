# Agent Flow Craft

Framework para automação de fluxo de criação de features usando agentes de IA.

## Instalação

### Instalação Rápida

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/agent-flow-craft.git
cd agent-flow-craft

# Criar ambiente virtual e instalar dependências
make install

# Para desenvolvimento, instalar dependências adicionais
make setup
```

### Configuração

1. Copie o arquivo `.env.example` para `.env`:
```bash
cp .env.example .env
```

2. Configure as variáveis de ambiente no arquivo `.env`:
```env
# Chaves de API
OPENAI_API_KEY=sua-chave-openai
OPENROUTER_API_KEY=sua-chave-openrouter
GOOGLE_API_KEY=sua-chave-google
GITHUB_TOKEN=seu-token-github

# Configurações de Modelos
DEFAULT_MODEL=gpt-4-turbo-preview
ELEVATION_MODEL=gpt-4-turbo-preview
FALLBACK_MODEL=claude-3-sonnet
```

## Uso

O pacote oferece vários comandos para automação de tarefas:

```bash
# Criar uma nova feature
agent-flow-craft feature --name "nome-da-feature" --description "descrição da feature"

# Gerar conceitos
agent-flow-craft concept --name "nome-do-conceito"

# Validar plano
agent-flow-craft validate --plan "plano-a-validar"

# Integração com GitHub
agent-flow-craft github --repo "usuario/repositorio"

# Gerar critérios TDD
agent-flow-craft tdd --feature "nome-da-feature"

# Verificar status do sistema
agent-flow-craft status
```

## Desenvolvimento

Para contribuir com o projeto:

```bash
# Instalar dependências de desenvolvimento
make setup

# Formatar código
make format

# Verificar código
make lint

# Executar testes
make test

# Limpar arquivos gerados
make clean
```

## Modelos Suportados

O framework suporta os seguintes provedores de modelos:

- OpenAI (GPT-4, GPT-3.5)
- OpenRouter (Claude, Mistral, etc)
- Google (Gemini)

O sistema possui um mecanismo de fallback que alterna automaticamente entre modelos em caso de falhas ou limites de quota.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
