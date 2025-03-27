.PHONY: pack deploy clean install test

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

# Empacotar o projeto
pack:
	@if [ -z "$(out)" ]; then \
		echo "Erro: Especifique o diretório de saída com --out=DIRECTORY"; \
		exit 1; \
	fi
	@echo "Empacotando projeto para $(out)..."
	@mkdir -p $(out)
	@rm -rf build/ dist/ *.egg-info/
	@python3 setup.py sdist bdist_wheel
	@cp dist/*.whl $(out)/agent_platform-$(VERSION)-py3-none-any.whl
	@cp -r agent_platform $(out)/agent_platform
	@echo "Copiando arquivo de configuração MCP..."
	@mkdir -p $(out)/config
	@echo '{' > $(out)/config/mcp.json
	@echo '  "mcpServers": {' >> $(out)/config/mcp.json
	@echo '    "local": {' >> $(out)/config/mcp.json
	@echo '      "name": "AgentFlow MCP",' >> $(out)/config/mcp.json
	@echo '      "type": "stdio",' >> $(out)/config/mcp.json
	@echo '      "config": {' >> $(out)/config/mcp.json
	@echo '        "command": "mcp_agent",' >> $(out)/config/mcp.json
	@echo '        "env": {' >> $(out)/config/mcp.json
	@echo '          "LOG_LEVEL": "DEBUG",' >> $(out)/config/mcp.json
	@echo '          "GITHUB_TOKEN": "seu_token_github",' >> $(out)/config/mcp.json
	@echo '          "OPENAI_API_KEY": "seu_token_openai",' >> $(out)/config/mcp.json
	@echo '          "GITHUB_OWNER": "seu_usuario_github",' >> $(out)/config/mcp.json
	@echo '          "GITHUB_REPO": "seu_repositorio"' >> $(out)/config/mcp.json
	@echo '        },' >> $(out)/config/mcp.json
	@echo '        "timeout": 30' >> $(out)/config/mcp.json
	@echo '      }' >> $(out)/config/mcp.json
	@echo '    }' >> $(out)/config/mcp.json
	@echo '  },' >> $(out)/config/mcp.json
	@echo '  "mcp_default_server": "local",' >> $(out)/config/mcp.json
	@echo '  "mcp_plugins": {' >> $(out)/config/mcp.json
	@echo '    "feature_creator": {' >> $(out)/config/mcp.json
	@echo '      "name": "Feature Creator",' >> $(out)/config/mcp.json
	@echo '      "description": "Cria novas features usando o MCP local",' >> $(out)/config/mcp.json
	@echo '      "server": "local",' >> $(out)/config/mcp.json
	@echo '      "commands": {' >> $(out)/config/mcp.json
	@echo '        "create_feature": {' >> $(out)/config/mcp.json
	@echo '          "description": "Cria uma nova feature no projeto",' >> $(out)/config/mcp.json
	@echo '          "parameters": {' >> $(out)/config/mcp.json
	@echo '            "prompt": {' >> $(out)/config/mcp.json
	@echo '              "type": "string",' >> $(out)/config/mcp.json
	@echo '              "description": "Descrição da feature a ser criada"' >> $(out)/config/mcp.json
	@echo '            }' >> $(out)/config/mcp.json
	@echo '          }' >> $(out)/config/mcp.json
	@echo '        }' >> $(out)/config/mcp.json
	@echo '      }' >> $(out)/config/mcp.json
	@echo '    }' >> $(out)/config/mcp.json
	@echo '  }' >> $(out)/config/mcp.json
	@echo '}' >> $(out)/config/mcp.json
	@echo "Criando script de instalação..."
	@echo '#!/bin/bash' > $(out)/install.sh
	@echo 'set -e' >> $(out)/install.sh
	@echo '' >> $(out)/install.sh
	@echo 'echo "Instalando AgentFlow MCP v$(VERSION)..."' >> $(out)/install.sh
	@echo '' >> $(out)/install.sh
	@echo '# Definir diretório de instalação' >> $(out)/install.sh
	@echo 'MCP_DIR="$$HOME/.cursor/mcp/agent_platform"' >> $(out)/install.sh
	@echo 'mkdir -p "$$MCP_DIR"' >> $(out)/install.sh
	@echo '' >> $(out)/install.sh
	@echo '# Instalar o pacote' >> $(out)/install.sh
	@echo 'pip install --target="$$MCP_DIR" ./agent_platform-$(VERSION)-py3-none-any.whl' >> $(out)/install.sh
	@echo '' >> $(out)/install.sh
	@echo '# Copiar configuração' >> $(out)/install.sh
	@echo 'cp -f ./config/mcp.json "$$HOME/.cursor/mcp.json"' >> $(out)/install.sh
	@echo '' >> $(out)/install.sh
	@echo 'echo "Instalação concluída! Reinicie o Cursor para usar o MCP."' >> $(out)/install.sh
	@chmod +x $(out)/install.sh
	@echo "Empacotamento concluído em $(out)"
	@echo "Execute 'cd $(out) && ./install.sh' para instalar"

# Implantar o projeto
deploy:
	@if [ -z "$(in)" ] || [ -z "$(out)" ]; then \
		echo "Erro: Especifique a origem e o destino com --in=FILE --out=DIR"; \
		exit 1; \
	fi
	@echo "Implantando $(in) para $(out)..."
	@mkdir -p $(out)
	@if [[ "$(in)" == *.zip ]] || [[ "$(in)" == *.tar.gz ]]; then \
		echo "Extraindo $(in) para $(out)..."; \
		if [[ "$(in)" == *.zip ]]; then \
			unzip -q -o "$(in)" -d "$(out)"; \
		else \
			tar -xzf "$(in)" -C "$(out)"; \
		fi; \
	elif [[ "$(in)" == *.whl ]]; then \
		echo "Instalando wheel $(in) para $(out)..."; \
		pip install --target="$(out)" "$(in)"; \
	else \
		echo "Copiando arquivos de $(in) para $(out)..."; \
		cp -r "$(in)"/* "$(out)"/; \
	fi
	@echo "Implantação concluída em $(out)"
	@echo "Não esqueça de reiniciar o Cursor para aplicar as alterações"

# Limpar arquivos temporários
clean:
	rm -rf build/ dist/ *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

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
	@echo "Instalação concluída! Reinicie o Cursor para usar o MCP." 