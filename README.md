# AgentFlowCraft

> Estrutura automatizada para criação, execução, avaliação e conformidade de múltiplos agentes de IA orientados a microtarefas, com registro e rastreamento completo.

---

## ⚡ Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/agent-flow-craft.git
cd agent-flow-craft

# Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Instale o pacote em modo de desenvolvimento
make install
```

## 🔐 Configuração de Variáveis de Ambiente

IMPORTANTE: Este projeto não utiliza arquivos .env por questões de segurança. Configure as variáveis diretamente no ambiente ou via argumentos de linha de comando.

### Variáveis Obrigatórias

```bash
# Configuração via ambiente (Linux/Mac)
export OPENAI_API_KEY="sua-chave-aqui"
export GITHUB_TOKEN="seu-token-aqui"
export GITHUB_OWNER="seu-usuario"
export GITHUB_REPO="seu-repositorio"

# Configuração via ambiente (Windows PowerShell)
$env:OPENAI_API_KEY="sua-chave-aqui"
$env:GITHUB_TOKEN="seu-token-aqui"
$env:GITHUB_OWNER="seu-usuario"
$env:GITHUB_REPO="seu-repositorio"
```

### Variáveis Opcionais para Provedores Adicionais

```bash
# Provedores de IA alternativos
export OPENROUTER_KEY="sua-chave-aqui"
export DEEPSEEK_KEY="sua-chave-aqui"
export GEMINI_KEY="sua-chave-aqui"

# Configurações de modelo padrão
export DEFAULT_MODEL="gpt-4-turbo"
export ELEVATION_MODEL="gpt-4"
export FALLBACK_ENABLED="true"

# Timeouts e retentativas
export MODEL_TIMEOUT="30"
export MAX_RETRIES="3"

# Cache
export CACHE_ENABLED="true"
export CACHE_TTL="3600"
export CACHE_DIR="./cache"

# Logging
export LOG_LEVEL="INFO"
export LOG_FILE="./logs/agent.log"
```

### Configuração por Modelo

Cada modelo pode ter suas próprias configurações específicas:

```bash
# OpenAI GPT-4 Turbo
export OPENAI_GPT_4_TURBO_TIMEOUT="30"
export OPENAI_GPT_4_TURBO_MAX_RETRIES="3"
export OPENAI_GPT_4_TURBO_TEMPERATURE="0.7"
export OPENAI_GPT_4_TURBO_MAX_TOKENS="4000"

# Claude 3 Opus via OpenRouter
export OPENROUTER_ANTHROPIC_CLAUDE_3_OPUS_TIMEOUT="30"
export OPENROUTER_ANTHROPIC_CLAUDE_3_OPUS_TEMPERATURE="0.7"
export OPENROUTER_ANTHROPIC_CLAUDE_3_OPUS_MAX_TOKENS="4000"

# DeepSeek Coder
export DEEPSEEK_DEEPSEEK_CODER_TIMEOUT="30"
export DEEPSEEK_DEEPSEEK_CODER_TEMPERATURE="0.7"
export DEEPSEEK_DEEPSEEK_CODER_MAX_TOKENS="4000"

# Gemini Pro
export GEMINI_GEMINI_PRO_TIMEOUT="30"
export GEMINI_GEMINI_PRO_TEMPERATURE="0.7"
export GEMINI_GEMINI_PRO_MAX_TOKENS="4000"
```

## 🚀 Uso via CLI

Todos os comandos aceitam parâmetros para sobrescrever as configurações de ambiente:

```bash
# Criar feature com configurações específicas
agent-flow-craft feature "Implementar sistema de notificações" \
  --model gpt-4-turbo \
  --elevation-model gpt-4 \
  --temperature 0.8 \
  --max-tokens 8000 \
  --timeout 60

# Gerar conceito com modelo específico
agent-flow-craft concept "Sistema de cache distribuído" \
  --model anthropic/claude-3-opus \
  --api-key "sua-chave-aqui"

# Validar plano com configurações personalizadas
agent-flow-craft validate plano.md \
  --model deepseek-coder \
  --temperature 0.5

# Integrar com GitHub usando modelo específico
agent-flow-craft github feature-123 \
  --model gemini-pro \
  --max-retries 5
```

## 📊 Status do Sistema

Verifique a configuração atual e modelos disponíveis:

```bash
agent-flow-craft status
```

## 🔄 Comandos Make

```bash
# Instalar o projeto
make install

# Executar testes
make test

# Limpar arquivos temporários
make clean

# Ver todos os comandos disponíveis
make help
```
