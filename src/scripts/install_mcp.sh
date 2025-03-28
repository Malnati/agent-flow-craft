#!/bin/bash
set -e

# Script de instalação do MCP para o Cursor IDE
# Executa todas as etapas necessárias, incluindo permissões

echo "=== Instalando AgentFlow MCP para Cursor IDE ==="

# Determinar diretórios
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CURSOR_DIR="$HOME/.cursor"
MCP_DIR="$CURSOR_DIR/mcp/agent_platform"

# Criar diretórios necessários
echo "Criando diretórios..."
mkdir -p "$CURSOR_DIR"
mkdir -p "$MCP_DIR"

# Instalar versão simplificada do MCP
echo "Instalando versão simplificada do MCP..."
cp -f "$SCRIPT_DIR/mcp_agent.py" "$CURSOR_DIR/"
chmod +x "$CURSOR_DIR/mcp_agent.py"

# Configurar arquivo MCP
echo "Configurando arquivo MCP..."
cat > "$CURSOR_DIR/mcp.json" << EOF
{
  "mcpServers": {
    "local": {
      "name": "AgentFlow MCP",
      "type": "stdio",
      "config": {
        "command": "$CURSOR_DIR/mcp_agent.py",
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
  "mcp_default_server": "local",
  "mcp_plugins": {
    "feature_creator": {
      "name": "Feature Creator",
      "description": "Cria novas features usando o MCP local",
      "server": "local",
      "commands": {
        "create_feature": {
          "description": "Cria uma nova feature no projeto",
          "parameters": {
            "prompt": {
              "type": "string",
              "description": "Descrição da feature a ser criada"
            }
          }
        }
      }
    }
  }
}
EOF

echo -e "\n=== Instalação concluída! ==="
echo "Para usar, edite $CURSOR_DIR/mcp.json e substitua:"
echo "- seu_token_github pelo seu token do GitHub"
echo "- seu_token_openai pelo seu token do OpenAI"
echo "- seu_usuario_github pelo seu usuário do GitHub"
echo "- seu_repositorio pelo nome do repositório"
echo -e "\nEm seguida, reinicie o Cursor e acesse 'MCP: Create Feature' pelo Command Palette."
echo -e "\nPara desinstalar o MCP, execute: ./agent_platform/scripts/uninstall_mcp.sh" 