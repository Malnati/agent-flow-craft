.PHONY: install setup test lint format start-agent update-docs-index clean clean-pycache all create-venv \
	pack deploy undeploy install-cursor install-simple-mcp help build publish version version-info find-commit update-changelog compare-versions test-mcp-e2e \
	start-concept-agent start-github-agent start-coordinator-agent start-context-manager start-validator

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
	@echo ""
	@echo "Agentes disponíveis:"
	@echo "  make start-agent prompt=\"...\" execution_plan=\"...\" target=\"...\"  Inicia o agente de criação de features (FeatureCoordinatorAgent)"
	@echo "  make start-concept-agent prompt=\"...\"        Inicia o agente de geração de conceitos (ConceptGenerationAgent)"
	@echo "  make start-github-agent context_id=\"...\"      Inicia o agente de integração com GitHub (GitHubIntegrationAgent)"
	@echo "  make start-coordinator-agent prompt=\"...\"    Inicia o agente coordenador (FeatureCoordinatorAgent)"
	@echo "  make start-context-manager operation=\"...\"   Executa operação do gerenciador de contexto (listar, obter, criar, etc.)"
	@echo "  make start-validator plan_file=\"...\"         Executa o validador de planos em um arquivo JSON"
	@echo ""
	@echo "Outros comandos:"
	@echo "  make pack --out=DIRECTORY     Empacota o projeto MCP para o diretório especificado"
	@echo "  make deploy                   Instala a última versão do pacote do PyPI e verifica a instalação"
	@echo "  make install-cursor           Instala no diretório MCP do Cursor"
	@echo "  make install-simple-mcp       Instala Simple MCP no Cursor"
	@echo "  make undeploy                 Remove o MCP do Cursor IDE"
	@echo "  make publish                  Publica o projeto no PyPI (requer PyPI_TOKEN)"
	@echo "  make version                  Mostra a versão que será usada na publicação"
	@echo "  make version-info version=X.Y.Z.devN  Mostra informações da versão especificada"
	@echo "  make find-commit version=X.Y.Z.devN   Retorna o hash do commit associado à versão"
	@echo "  make update-changelog version=X.Y.Z.devN  Atualiza o CHANGELOG.md com informações da versão"
	@echo "  make compare-versions from=X.Y.Z.devN to=X.Y.Z.devN  Compara as mudanças entre duas versões"
	@echo "  make test-mcp-e2e              Executa o teste e2e do MCP"

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

# Target para iniciar o agente conceito (ConceptGenerationAgent)
start-concept-agent: create-venv print-no-pycache-message
	@if [ -z "$(prompt)" ]; then \
		echo "Uso: make start-concept-agent prompt=\"<descricao>\" [output=\"<arquivo_saida>\"]"; \
		exit 1; \
	fi
	@echo "Executando agente de conceito com prompt: \"$(prompt)\""
	@$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python -B src/scripts/run_concept_agent.py \
		"$(prompt)" \
		$(if $(output),--output "$(output)",) \
		$(if $(git_log_file),--git_log_file "$(git_log_file)",)

# Target para iniciar o agente GitHub (GitHubIntegrationAgent)
start-github-agent: create-venv print-no-pycache-message
	@if [ -z "$(context_id)" ]; then \
		echo "Uso: make start-github-agent context_id=\"<id_do_contexto>\" [target=\"<diretorio_git>\"]"; \
		exit 1; \
	fi
	@echo "Executando agente GitHub com contexto: \"$(context_id)\""
	@if [ ! -z "$(target)" ]; then \
		echo "Diretório alvo: \"$(target)\""; \
	fi
	@$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python -B src/scripts/run_github_agent.py \
		"$(context_id)" \
		$(if $(target),--target "$(target)",) \
		$(if $(output),--output "$(output)",)

# Target para iniciar o agente coordenador (FeatureCoordinatorAgent)
start-coordinator-agent: create-venv print-no-pycache-message
	@if [ -z "$(prompt)" ]; then \
		echo "Uso: make start-coordinator-agent prompt=\"<descricao>\" [plan_file=\"<arquivo_plano>\"] [target=\"<diretorio_git>\"] [output=\"<arquivo_saida>\"]"; \
		exit 1; \
	fi
	@echo "Executando agente coordenador com prompt: \"$(prompt)\""
	@if [ ! -z "$(target)" ]; then \
		echo "Diretório alvo: \"$(target)\""; \
	fi
	@if [ ! -z "$(plan_file)" ]; then \
		echo "Arquivo de plano: \"$(plan_file)\""; \
		$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python -B src/scripts/start_feature_agent.py \
			"$(prompt)" \
			"$(plan_file)" \
			$(if $(target),--target "$(target)",) \
			$(if $(output),--output "$(output)",); \
	else \
		$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python -B src/scripts/start_feature_agent.py \
			"$(prompt)" \
			$(if $(target),--target "$(target)",) \
			$(if $(output),--output "$(output)",); \
	fi

# Target para gerenciador de contexto (ContextManager)
start-context-manager: create-venv print-no-pycache-message
	@if [ -z "$(operation)" ]; then \
		echo "Uso: make start-context-manager operation=<lista|obter|criar|atualizar|excluir> [context_id=\"<id>\"] [data_file=\"<arquivo.json>\"] [limit=10] [type=\"<tipo>\"]"; \
		echo "Operações disponíveis:"; \
		echo "  lista   - Lista contextos. Opções: [limit=10] [type=\"tipo\"]"; \
		echo "  obter   - Obtém um contexto. Requer: context_id=\"id\""; \
		echo "  criar   - Cria um contexto. Requer: data_file=\"arquivo.json\" [type=\"tipo\"]"; \
		echo "  atualizar - Atualiza um contexto. Requer: context_id=\"id\" data_file=\"arquivo.json\" [merge=true|false]"; \
		echo "  excluir - Exclui um contexto. Requer: context_id=\"id\""; \
		echo "  limpar  - Remove contextos antigos. Opções: [days=7]"; \
		exit 1; \
	fi
	@echo "Executando gerenciador de contexto com operação: \"$(operation)\""
	@$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python -B src/scripts/run_context_manager.py \
		"$(operation)" \
		$(if $(context_id),--context_id "$(context_id)",) \
		$(if $(data_file),--data_file "$(data_file)",) \
		$(if $(type),--type "$(type)",) \
		$(if $(limit),--limit $(limit),) \
		$(if $(days),--days $(days),) \
		$(if $(merge),--merge $(merge),) \
		$(if $(output),--output "$(output)",)

# Target para validador de planos (PlanValidator)
start-validator: create-venv print-no-pycache-message
	@if [ -z "$(plan_file)" ]; then \
		echo "Uso: make start-validator plan_file=\"<arquivo_plano.json>\" [output=\"<arquivo_saida>\"]"; \
		exit 1; \
	fi
	@echo "Executando validador de planos com arquivo: \"$(plan_file)\""
	@$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python -B src/scripts/run_plan_validator.py \
		"$(plan_file)" \
		$(if $(requirements),--requirements "$(requirements)",) \
		$(if $(output),--output "$(output)",)

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

# Target para iniciar o agente de feature
start-agent: check-env create-venv print-no-pycache-message
	@if [ -z "$(prompt)" ] || [ -z "$(execution_plan)" ] || [ -z "$(target)" ]; then \
		echo "Uso: make start-agent prompt=\"<descricao>\" execution_plan=\"<plano de execucao>\" target=\"<target>\""; \
		exit 1; \
	fi
	@# Criar versão segura dos argumentos sem exibir tokens
	@echo "Executando agente com prompt: \"$(prompt)\""
	@echo "Diretório alvo: \"$(target)\""
	@echo "Executando comando com argumentos sensíveis mascarados..."
	@# Executar o comando sem exibir tokens
	@$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python -B src/scripts/start_feature_agent.py \
		"$(prompt)" \
		"$(execution_plan)" \
		--target "$(target)" \
		$(ARGS)

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
deploy: create-venv
	@echo "\n🚀 Instalando a última versão do pacote agent-flow-craft do PyPI..."
	$(ACTIVATE) && $(PYTHON_ENV) pip install --upgrade --force-reinstall agent-flow-craft
	@echo "\n🔍 Verificando se a instalação foi bem-sucedida..."
	@echo "📦 Versão instalada:"
	@$(ACTIVATE) && $(PYTHON_ENV) pip list | grep -i agent-flow-craft || (echo "❌ Erro: O pacote agent-flow-craft não parece estar instalado." && exit 1)
	@echo "\n⚙️ Verificando importação do pacote..."
	@$(ACTIVATE) && $(PYTHON_ENV) python -c "import importlib.util; spec = importlib.util.find_spec('agent_platform'); print('✅ Pacote importado: ' + spec.origin if spec is not None else '❌ Erro: Não foi possível importar o pacote agent_platform.'); exit(1 if spec is None else 0)"
	@echo "\n✅ Implantação concluída com sucesso!"

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

# Executar teste e2e do MCP
test-mcp-e2e: create-venv
	@echo "\n🧪 Executando teste e2e para o MCP..."
	@echo "\n🔧 Configurando ambiente de teste..."
	$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python src/scripts/setup_mcp_test.py
	@echo "\n🚀 Executando teste..."
	$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python src/tests/test_mcp_e2e.py
	@echo "\n✅ Teste e2e do MCP concluído!"

# Atualizar o CHANGELOG.md com a nova versão
update-changelog:
	@if [ -z "$(version)" ]; then \
		echo "Uso: make update-changelog version=X.Y.Z.devN"; \
		exit 1; \
	fi
	@if [ ! -f "version_commits.json" ]; then \
		echo "Erro: Arquivo de mapeamento version_commits.json não encontrado."; \
		exit 1; \
	fi
	@echo "Atualizando CHANGELOG.md com a versão $(version)..."
	@$(PYTHON) -c "import json; import os; import time; v='$(version)'; \
		data = json.load(open('version_commits.json')); \
		if v not in data: \
			print('Versão não encontrada no arquivo de mapeamento.'); \
			exit(1); \
		commit = data[v]['commit_hash']; \
		timestamp = data[v]['timestamp']; \
		changelog_content = ''; \
		if os.path.exists('CHANGELOG.md'): \
			with open('CHANGELOG.md', 'r') as f: \
				changelog_content = f.read(); \
		if not changelog_content: \
			changelog_content = '# Changelog\\n\\nTodas as mudanças notáveis do projeto serão documentadas neste arquivo.\\n\\n'; \
		import subprocess; \
		try: \
			commit_msg = subprocess.check_output(['git', 'log', '-1', '--pretty=%B', commit]).decode('utf-8').strip(); \
		except: \
			commit_msg = 'Commit message not available'; \
		entry = f'## {v} ({timestamp.split()[0]})\\n\\n' + \
				f'**Commit:** {commit}\\n\\n' + \
				f'**Mensagem de commit:** {commit_msg}\\n\\n' + \
				f'---\\n\\n'; \
		if '## ' in changelog_content: \
			parts = changelog_content.split('## ', 1); \
			new_content = parts[0] + entry + '## ' + parts[1]; \
		else: \
			new_content = changelog_content + entry; \
		with open('CHANGELOG.md', 'w') as f: \
			f.write(new_content); \
		print('CHANGELOG.md atualizado com sucesso.')"

# Publicar no PyPI e atualizar CHANGELOG
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
	@echo "A versão do pacote será gerada como: YYYY.MM.DD.devN"
	@echo "Onde N é um número único derivado do timestamp e hash do commit."
	@echo "Este formato é totalmente compatível com PEP 440 e aceito pelo PyPI."
	@echo "Se quiser definir uma versão específica, use: VERSION=1.2.3 make publish"
	$(ACTIVATE) && $(PYTHON_ENV) TWINE_USERNAME=__token__ TWINE_PASSWORD=$(PyPI_TOKEN) python -m twine upload dist/*
	@echo "Publicação concluída!"
	@VERSION=$$(python -c "import subprocess; print(subprocess.check_output(['pip', 'show', 'agent_flow_craft']).decode().split('Version: ')[1].split('\\n')[0] if 'agent_flow_craft' in subprocess.check_output(['pip', 'freeze']).decode() else 'Não instalado localmente')")
	@echo "Versão publicada: $$VERSION"
	@if [ -f "version_commits.json" ] && [ ! -z "$$VERSION" ]; then \
		echo ""; \
		echo "Informações de rastreabilidade:"; \
		$(PYTHON) -c "import json; import sys; v='$$VERSION'; \
			data = json.load(open('version_commits.json')); \
			if v in data: \
				print(f'  Commit associado: {data[v][\"commit_hash\"]}'); \
				print(f'  Data/hora do build: {data[v][\"timestamp\"]}'); \
				print(f'\nPara visualizar as mudanças deste commit, execute:'); \
				print(f'  git show {data[v][\"commit_hash\"]}'); \
			else: \
				print(f'  Versão {v} não encontrada no arquivo de mapeamento.')"; \
		make update-changelog version=$$VERSION; \
	fi

# Adiciona o lembrete a todos os comandos principais
install setup test lint format start-agent update-docs-index publish: print-no-pycache-message 

# Verificar a versão que será publicada
version:
	@echo "Versão que será publicada:"
	@$(PYTHON) -c "import subprocess; import time; import re; def simple_slugify(text, separator=''): text = re.sub(r'[^\w\s-]', '', text.lower()); text = re.sub(r'[-\s]+', separator, text).strip('-'); return text; try: commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip(); hash_num = 0; for i, c in enumerate(commit_hash[:4]): hash_num += ord(c) * (10 ** i); hash_num = hash_num % 1000; except (subprocess.SubprocessError, FileNotFoundError): hash_num = int(time.time()) % 1000; timestamp = time.strftime('%H%M%S'); year_month = time.strftime('%Y.%m'); day = time.strftime('%d'); dev_num = int(timestamp[:4] + str(hash_num).zfill(3)); print(f'{year_month}.{day}.dev{dev_num}')"
	@echo ""
	@echo "Formato: MAJOR.MINOR.PATCH.devN (PEP 440 compatível)"
	@echo "  • MAJOR.MINOR = ano.mês (2025.03)"
	@echo "  • PATCH = dia (28)"
	@echo "  • N = número derivado do timestamp e hash do commit (10150123)"
	@echo ""
	@echo "Para definir manualmente a versão, use:"
	@echo "VERSION=1.2.3 make publish    # Será expandido para 1.2.3.devXXXXX"

# Obter informações de uma versão específica (commit hash, etc)
version-info:
	@if [ -z "$(version)" ]; then \
		echo "Uso: make version-info version=X.Y.Z.devN"; \
		echo "Exemplo: make version-info version=2025.3.28.dev1020131"; \
		exit 1; \
	fi
	@if [ ! -f "version_commits.json" ]; then \
		echo "Erro: Arquivo de mapeamento version_commits.json não encontrado."; \
		echo "Este arquivo é gerado durante o build do pacote."; \
		exit 1; \
	fi
	@$(PYTHON) -c "import json; v='$(version)'; \
		data = json.load(open('version_commits.json')); \
		if v in data: \
			print(f'\nInformações da versão {v}:'); \
			print(f'  Commit hash: {data[v][\"commit_hash\"]}'); \
			print(f'  Data/hora: {data[v][\"timestamp\"]}'); \
			print(f'  Build number: {data[v][\"build_number\"]}'); \
			print(f'\nPara ver as mudanças deste commit:'); \
			print(f'  git show {data[v][\"commit_hash\"]}'); \
		else: \
			print(f'Versão {v} não encontrada no arquivo de mapeamento.')"

# Encontrar o commit associado a uma versão
find-commit:
	@if [ -z "$(version)" ]; then \
		echo "Uso: make find-commit version=X.Y.Z.devN"; \
		echo "Exemplo: make find-commit version=2025.3.28.dev1020131"; \
		exit 1; \
	fi
	@if [ ! -f "version_commits.json" ]; then \
		echo "Erro: Arquivo de mapeamento version_commits.json não encontrado."; \
		echo "Este arquivo é gerado durante o build do pacote."; \
		exit 1; \
	fi
	@$(PYTHON) -c "import json; v='$(version)'; \
		data = json.load(open('version_commits.json')); \
		if v in data: \
			print(data[v]['commit_hash']); \
		else: \
			print('NOTFOUND'); \
			exit(1)"

# Comparar duas versões (mostrar diferenças de commits)
compare-versions:
	@if [ -z "$(from)" ] || [ -z "$(to)" ]; then \
		echo "Uso: make compare-versions from=X.Y.Z.devN to=X.Y.Z.devN"; \
		echo "Exemplo: make compare-versions from=2025.3.28.dev1020023 to=2025.3.28.dev1020131"; \
		exit 1; \
	fi
	@if [ ! -f "version_commits.json" ]; then \
		echo "Erro: Arquivo de mapeamento version_commits.json não encontrado."; \
		exit 1; \
	fi
	@$(PYTHON) -c "import json; \
		from_v='$(from)'; to_v='$(to)'; \
		data = json.load(open('version_commits.json')); \
		if from_v not in data: \
			print(f'Versão inicial {from_v} não encontrada no arquivo de mapeamento.'); \
			exit(1); \
		if to_v not in data: \
			print(f'Versão final {to_v} não encontrada no arquivo de mapeamento.'); \
			exit(1); \
		from_commit = data[from_v]['commit_hash']; \
		to_commit = data[to_v]['commit_hash']; \
		import subprocess; \
		print(f'\nMudanças entre {from_v} e {to_v}:\n'); \
		print(f'Commits: {from_commit}..{to_commit}\n'); \
		print('Para ver as diferenças entre essas versões, execute:'); \
		print(f'  git diff {from_commit} {to_commit}\n'); \
		print('Lista de commits entre as versões:'); \
		try: \
			log = subprocess.check_output(['git', 'log', '--oneline', f'{from_commit}..{to_commit}']).decode('utf-8'); \
			print(log); \
		except Exception as e: \
			print(f'Erro ao obter log de commits: {e}')" 