.PHONY: pack deploy clean install test undeploy start-agent agent-platform-commands

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
	@echo "  make start-agent prompt=\"...\" execution_plan=\"...\"  Inicia o agente de criação de features"

# Empacotar o projeto
pack:
ifndef out
	$(error Por favor especifique um diretório de saída: make pack out=DIRECTORY)
endif
	@echo "Empacotando projeto MCP na versão $(VERSION)..."
	@mkdir -p $(BUILD_DIR)
	@mkdir -p $(out)
	@rm -rf $(BUILD_DIR)/*
	@python setup.py bdist_wheel
	@cp -f $(BUILD_DIR)/*.whl $(out)/
	@cp -f .cursor/config.json $(out)/
	@echo '#!/bin/bash\npip install *.whl\ncp -f config.json $(HOME)/.cursor/mcp.json\necho "Instalação concluída! Reinicie o Cursor para usar o MCP."' > $(out)/install.sh
	@chmod +x $(out)/install.sh
	@echo "Empacotamento concluído! Arquivos disponíveis em: $(out)"

# Implantar o pacote
deploy:
ifndef in
	$(error Por favor especifique um arquivo de entrada: make deploy in=FILE out=DIRECTORY)
endif
ifndef out
	$(error Por favor especifique um diretório de saída: make deploy in=FILE out=DIRECTORY)
endif
	@echo "Implantando pacote $(in) no diretório $(out)..."
	@mkdir -p $(out)
	@if [[ "$(in)" == *.zip ]]; then unzip -o $(in) -d $(out); \
	elif [[ "$(in)" == *.tar.gz ]]; then tar -xzf $(in) -C $(out); \
	elif [[ "$(in)" == *.whl ]]; then pip install $(in) --target=$(out); \
	else cp -r $(in)/* $(out)/; fi
	@echo "Implantação concluída!"

# Limpar arquivos temporários e de build
clean:
	@echo "Limpando arquivos temporários e de build..."
	@rm -rf build/
	@rm -rf $(BUILD_DIR)/
	@rm -rf *.egg-info/
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "Limpeza concluída!"

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

# Instalação simplificada do MCP
install-simple-mcp:
	@echo "Instalando Simple MCP no Cursor..."
	@mkdir -p $(HOME)/.cursor/
	@cp -f .cursor/agents/mcp_agent.py $(HOME)/.cursor/
	@cp -f .cursor/agents/mcp_simple.json $(HOME)/.cursor/mcp.json
	@echo "Simple MCP instalado com sucesso! Reinicie o Cursor para utilizá-lo."

# Remover o MCP do Cursor
undeploy:
	@echo "Removendo MCP do Cursor IDE..."
	@rm -f $(HOME)/.cursor/mcp.json
	@rm -f $(HOME)/.cursor/mcp_agent.py
	@rm -rf $(HOME)/.cursor/mcp/agent_platform
	@echo "MCP removido com sucesso!"

# Comandos da Agent Platform
# Inicia o agente com os parâmetros fornecidos
start-agent:
	@if [ -z "$(prompt)" ] || [ -z "$(execution_plan)" ]; then \
		echo "Uso: make start-agent prompt=\"<descricao>\" execution_plan=\"<plano de execucao>\""; \
		exit 1; \
	fi
	@echo "Iniciando agente de criação de features..."
	@cd agent_platform && $(MAKE) start-agent prompt="$(prompt)" execution_plan="$(execution_plan)" \
		GITHUB_TOKEN="$(GITHUB_TOKEN)" GITHUB_OWNER="$(GITHUB_OWNER)" \
		GITHUB_REPO="$(GITHUB_REPO)" OPENAI_TOKEN="$(OPENAI_TOKEN)"

# Passa qualquer comando para o Makefile do agent_platform
agent-platform-commands:
	@cd agent_platform && $(MAKE) $(MAKECMDGOALS)
	
# Alvos que serão redirecionados para o Makefile do agent_platform
lint format update-docs-index: agent-platform-commands 