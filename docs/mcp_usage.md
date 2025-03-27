# Guia de Uso do MCP com Cursor

Este guia explica como empacotar, implantar e usar o AgentFlow MCP com o Cursor IDE.

## Índice
1. [Instalação Rápida](#instalação-rápida)
2. [Empacotamento e Implantação](#empacotamento-e-implantação)
3. [Configuração](#configuração)
4. [Uso no Cursor](#uso-no-cursor)
5. [Comandos Disponíveis](#comandos-disponíveis)

## Instalação Rápida

Para uma instalação rápida e simplificada:

```bash
# Método 1: Usando o script de instalação
./scripts/install_mcp.sh

# Método 2: Usando o make
make install-simple-mcp
```

Após a instalação, configure suas credenciais em `~/.cursor/mcp.json` e reinicie o Cursor.

## Empacotamento e Implantação

### Opção 1: Empacotamento Automatizado

Para empacotar e criar um instalador:

```bash
# Instala dependências de desenvolvimento
pip install -e .[dev]

# Empacota para o diretório de saída
make pack --out=./mcp_package

# Para instalar o pacote
cd ./mcp_package
./install.sh
```

### Opção 2: Implantação Direta

Para implantar diretamente no Cursor:

```bash
# Instala diretamente no diretório do Cursor
make install-cursor
```

### Opção 3: Implantação de Pacote Existente

Para implantar um pacote existente:

```bash
# Implanta um wheel ou pacote existente
make deploy --in=./mcp_package/agent_platform-2023.03.27-py3-none-any.whl --out=$HOME/.cursor/mcp/agent_platform
```

## Configuração

Após a instalação, edite o arquivo de configuração em `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "local": {
      "name": "AgentFlow MCP",
      "type": "stdio",
      "config": {
        "command": "~/.cursor/mcp_agent.py",
        "env": {
          "LOG_LEVEL": "DEBUG",
          "GITHUB_TOKEN": "seu_token_github",
          "OPENAI_API_KEY": "seu_token_openai",
          "GITHUB_OWNER": "seu_usuario_github",
          "GITHUB_REPO": "seu_repositorio"
        },
        "timeout": 30
      }
    }
  },
  "mcp_default_server": "local"
}
```

Substitua os valores `seu_token_github`, `seu_token_openai`, `seu_usuario_github`, e `seu_repositorio` pelos valores reais.

## Uso no Cursor

Após instalação e configuração:

1. Reinicie o Cursor IDE
2. Abra o Command Palette (Cmd+Shift+P / Ctrl+Shift+P)
3. Digite "MCP: Create Feature"
4. Forneça a descrição da feature a ser criada

## Comandos Disponíveis

O MCP suporta os seguintes comandos:

### Create Feature

Cria uma nova feature no projeto, incluindo:

- Criação de issue no GitHub
- Criação de branch
- Plano de execução
- PR inicial

**Parâmetros:**
- `prompt`: Descrição detalhada da feature a ser implementada

**Exemplo:**
```
Implementar sistema de autenticação MCP

Requisitos:
- Integração com OAuth2
- Suporte a múltiplos providers
- Sistema de cache de tokens
- Renovação automática de credenciais
```

### Heartbeat

Verifica se o MCP está funcionando corretamente.

## Solução de Problemas

Se encontrar problemas:

1. Verifique os logs em `~/.cursor/mcp_agent.log`
2. Confirme se os tokens de acesso estão corretos
3. Verifique se o script tem permissão de execução
4. Reinicie o Cursor IDE

Para mais informações, consulte a [documentação oficial do Cursor](https://cursor.sh/docs/plugins/mcp). 