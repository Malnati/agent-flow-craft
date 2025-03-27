#!/bin/bash

# Criar um Makefile novo com tabulações corretas
cat > Makefile.new << 'EOF'
.PHONY: pack deploy clean install test undeploy

VERSION := $(shell python3 -c "import time; print(time.strftime('%Y.%m.%d'))")
BUILD_DIR := ./dist

# Ajuda do Makefile
help:
	@echo "Comandos disponíveis:"
	@echo "  make pack --out=DIRECTORY     Empacota o projeto MCP para o diretório especificado"
	@echo "  make deploy --in=FILE --out=DIR  Implanta o MCP empacotado no diretório alvo"
	@echo "  make clean                    Remove arquivos temporários e de build"
	@echo "  make install                  Instala o projeto no ambiente atual"
	@echo "  make test                     Executa os testes do projeto"
	@echo "  make undeploy                 Remove o MCP do Cursor IDE"

# Instalar localmente para desenvolvimento
install:
	pip install -e .

# Testar o projeto
test:
	pytest

# Instalar no diretório do MCP do Cursor
install-cursor:
	@echo "Instalando no diretório MCP do Cursor..."
	@mkdir -p $(HOME)/.cursor/mcp/agent_platform
	@pip install -e . --target=$(HOME)/.cursor/mcp/agent_platform
	@echo "Configurando arquivo MCP..."
	@cp -f .cursor/config.json $(HOME)/.cursor/mcp.json
	@echo "Configurando permissões de execução..."
	@chmod +x $(HOME)/.cursor/mcp/agent_platform/mcp_agent
	@echo "Instalação concluída! Reinicie o Cursor para usar o MCP."

# Remover o MCP do Cursor
undeploy:
	@echo "Removendo MCP do Cursor IDE..."
	@rm -f $(HOME)/.cursor/mcp.json
	@rm -f $(HOME)/.cursor/mcp_agent.py
	@rm -rf $(HOME)/.cursor/mcp/agent_platform
	@echo "MCP removido com sucesso!"
EOF

# Substituir o Makefile original pelo novo
mv Makefile.new Makefile

echo "Makefile corrigido com sucesso!" 