#!/bin/bash
set -e

# Script de desinstalação do MCP do Cursor IDE
echo "=== Removendo AgentFlow MCP do Cursor IDE ==="

# Determinar diretórios
CURSOR_DIR="$HOME/.cursor"
MCP_DIR="$CURSOR_DIR/mcp/agent_platform"

# Remover arquivos e diretórios
echo "Removendo arquivos de configuração e scripts..."
rm -f "$CURSOR_DIR/mcp.json"
rm -f "$CURSOR_DIR/mcp_agent.py"

echo "Removendo diretório MCP..."
rm -rf "$MCP_DIR"

echo "Removendo logs..."
rm -f "$CURSOR_DIR/mcp_agent.log"

echo -e "\n=== Desinstalação concluída! ==="
echo "O MCP foi removido do Cursor IDE."
echo "Reinicie o Cursor para aplicar as alterações." 