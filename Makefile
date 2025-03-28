.PHONY: install setup test lint format start-agent update-docs-index clean clean-pycache all create-venv \
	pack deploy undeploy install-cursor install-simple-mcp help build publish version

VERSION := $(shell python3 -c "import time; print(time.strftime('%Y.%m.%d'))")
BUILD_DIR := ./dist

# Define variáveis para o ambiente Python
VENV_DIR := .venv
PYTHON := python3
ACTIVATE := . $(VENV_DIR)/bin/activate
PYTHON_ENV := PYTHONDONTWRITEBYTECODE=1

# Ajuda do Makefile
help:
	@echo "Comandos disponíveis:"
	@echo "  make create-venv              Cria ambiente virtual Python se não existir"
	@echo "  make install                  Instala o projeto no ambiente virtual"
	@echo "  make setup                    Instala o projeto em modo de desenvolvimento"
	@echo "  make test                     Executa os testes do projeto"
	@echo "  make lint                     Executa análise de lint para verificar estilo de código"
	@echo "  make format                   Formata o código usando o Black"
	@echo "  make build                    Empacota o projeto usando python -m build"
	@echo "  make clean                    Remove arquivos temporários e de build"
	@echo "  make clean-pycache            Remove apenas os diretórios __pycache__ e arquivos .pyc"
	@echo "  make all                      Executa lint, test, formatação e atualização de docs"
	@echo "  make update-docs-index        Atualiza o índice da documentação automaticamente"
	@echo "  make start-agent prompt=\"...\" execution_plan=\"...\"  Inicia o agente de criação de features"
	@echo "  make pack --out=DIRECTORY     Empacota o projeto MCP para o diretório especificado"
	@echo "  make deploy --in=FILE --out=DIR  Implanta o MCP empacotado no diretório alvo"
	@echo "  make install-cursor           Instala no diretório MCP do Cursor"
	@echo "  make install-simple-mcp       Instala Simple MCP no Cursor"
	@echo "  make undeploy                 Remove o MCP do Cursor IDE"
	@echo "  make publish                  Publica o projeto no PyPI (requer PyPI_TOKEN)"
	@echo "  make version                  Mostra a versão que será usada na publicação"

# Verifica se ambiente virtual existe e cria se necessário
create-venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Criando ambiente virtual Python..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
		$(ACTIVATE) && pip install --upgrade pip; \
		$(ACTIVATE) && pip install pyyaml requests click pyautogen openai python-slugify; \
		echo "export PYTHONDONTWRITEBYTECODE=1" >> $(VENV_DIR)/bin/activate; \
	else \
		echo "Ambiente virtual já existe."; \
		$(ACTIVATE) && pip install -q pyyaml requests click pyautogen openai python-slugify; \
	fi

check-env:
	@if [ -z "$(GITHUB_TOKEN)" ]; then \
		echo "Erro: Variável de ambiente GITHUB_TOKEN não definida."; \
		exit 1; \
	fi
	@if [ -z "$(GITHUB_OWNER)" ]; then \
		echo "Erro: Variável de ambiente GITHUB_OWNER não definida."; \
		exit 1; \
	fi
	@if [ -z "$(GITHUB_REPO)" ]; then \
		echo "Erro: Variável de ambiente GITHUB_REPO não definida."; \
		exit 1; \
	fi
	@if [ -z "$(OPENAI_TOKEN)" ]; then \
		echo "Erro: Variável de ambiente OPENAI_TOKEN não definida."; \
		exit 1; \
	fi

# Instala as dependências do projeto via uv
install: create-venv
	$(ACTIVATE) && $(PYTHON_ENV) uv pip install -e . && uv pip install -e .[dev]

# Instala as dependências do projeto em modo de desenvolvimento
setup: create-venv
	$(ACTIVATE) && $(PYTHON_ENV) uv pip install -e .[dev]

# Executa todos os testes unitários
test: create-venv
	$(ACTIVATE) && $(PYTHON_ENV) python -m unittest discover -s tests

# Executa análise de lint para verificar problemas de estilo de código
lint: create-venv
	$(ACTIVATE) && $(PYTHON_ENV) flake8 .

# Formata o código usando o Black
format: create-venv
	$(ACTIVATE) && $(PYTHON_ENV) black .

# Empacota o projeto usando python -m build
build: create-venv
	@echo "Limpando diretório de distribuição..."
	@rm -rf $(BUILD_DIR)
	@mkdir -p $(BUILD_DIR)
	@echo "Construindo pacote..."
	$(ACTIVATE) && $(PYTHON_ENV) python -m build

# Exemplo de uso:
# make start-agent prompt="Descrição da feature" execution_plan="Plano detalhado de execução"
start-agent: check-env create-venv
	@if [ -z "$(prompt)" ] || [ -z "$(execution_plan)" ]; then \
		echo "Uso: make start-agent prompt=\"<descricao>\" execution_plan=\"<plano de execucao>\""; \
		exit 1; \
	fi
	$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python src/scripts/start_feature_agent.py "$(prompt)" "$(execution_plan)" --token "$(GITHUB_TOKEN)" --owner "$(GITHUB_OWNER)" --repo "$(GITHUB_REPO)" --openai_token "$(OPENAI_TOKEN)"

# Atualiza o índice da documentação automaticamente
update-docs-index: create-venv
	$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python src/scripts/generate_docs_index.py

# Limpa todos os arquivos __pycache__ e .pyc
clean-pycache:
	@echo "Removendo arquivos __pycache__ e .pyc..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@echo "Limpeza concluída!"

# Limpa todos os arquivos temporários
clean: clean-pycache
	@echo "Limpando arquivos temporários e de build..."
	@find . -type d -name "*.dist-info" -exec rm -rf {} +
	@find . -type d -name "build" -exec rm -rf {} +
	@rm -rf $(BUILD_DIR)/
	@rm -rf *.egg-info/
	@echo "Limpeza concluída!"

# Executa lint, test, formatação e atualização de docs
all: lint test format update-docs-index

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

# Instalar no diretório do MCP do Cursor
install-cursor:
	@echo "Instalando no diretório MCP do Cursor..."
	@mkdir -p $(HOME)/.cursor/mcp/src
	@pip install -e . --target=$(HOME)/.cursor/mcp/src
	@echo "Configurando arquivo MCP..."
	@cp -f .cursor/config.json $(HOME)/.cursor/mcp.json
	@echo "Configurando permissões de execução..."
	@chmod +x $(HOME)/.cursor/mcp/src/mcp_agent
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
	@rm -rf $(HOME)/.cursor/mcp/src
	@echo "MCP removido com sucesso!"

# Adiciona uma mensagem ao final para lembrar de compilação
print-no-pycache-message:
	@echo "======================================================="
	@echo "LEMBRETE: Arquivos .pyc e diretórios __pycache__ estão desabilitados"
	@echo "Para executar scripts manualmente, prefira usar:"
	@echo "python -B seu_script.py"
	@echo "ou defina a variável de ambiente PYTHONDONTWRITEBYTECODE=1"
	@echo "======================================================="

# Publicar no PyPI
publish: build
	@if [ -z "$(PyPI_TOKEN)" ]; then \
		echo "Erro: Variável de ambiente PyPI_TOKEN não definida."; \
		echo "Você precisa ter uma conta ativa no PyPI e uma chave de API."; \
		echo "Obtenha uma chave em https://pypi.org/manage/account/token/ e execute:"; \
		echo "export PyPI_TOKEN=seu_token_aqui"; \
		exit 1; \
	fi
	@echo "Instalando twine no ambiente virtual..."
	$(ACTIVATE) && $(PYTHON_ENV) pip install twine
	@echo "Publicando no PyPI..."
	@echo "A versão do pacote será gerada automaticamente com o formato: YYYY.MM.DD.HHMMSS.devCOMMIT_HASH"
	@echo "Este formato é compatível com PEP 440 e aceito pelo PyPI."
	@echo "Se quiser definir uma versão específica, use: VERSION=1.2.3 make publish"
	$(ACTIVATE) && $(PYTHON_ENV) TWINE_USERNAME=__token__ TWINE_PASSWORD=$(PyPI_TOKEN) python -m twine upload dist/*
	@echo "Publicação concluída!"
	@echo "Versão publicada: $(shell python -c "import subprocess; print(subprocess.check_output(['pip', 'show', 'agent_flow_craft']).decode().split('Version: ')[1].split('\\n')[0] if 'agent_flow_craft' in subprocess.check_output(['pip', 'freeze']).decode() else 'Não instalado localmente')")"

# Adiciona o lembrete a todos os comandos principais
install setup test lint format start-agent update-docs-index publish: print-no-pycache-message 

# Verificar a versão que será publicada
version:
	@echo "Versão que será publicada:"
	@$(PYTHON) -c "import subprocess; import time; from slugify import slugify; hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip(); build = time.strftime('%H%M%S'); print(f'{time.strftime(\"%Y.%m.%d\")}.{build}.dev{slugify(hash, separator=\"\")}')"
	@echo ""
	@echo "Formato: MAJOR.MINOR.PATCH.BUILD.devCOMMIT_HASH (PEP 440 compatível)"
	@echo ""
	@echo "Para definir manualmente a versão, use:"
	@echo "VERSION=1.2.3 make publish    # Será expandido para 1.2.3.dev<commit_hash_slugify>" 