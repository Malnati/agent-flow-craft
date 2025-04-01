.PHONY: install lint format clean all create-venv \
	pack deploy undeploy help build publish version version-info update-changelog compare-versions \
	start-github-agent prompt-creator setup-env clean-cache clean-pycache autoflake \
	start-refactor-agent test test-coverage clean-code cli-test

VERSION := $(shell python3 -c "import time; print(time.strftime('%Y.%m.%d'))")
BUILD_DIR := ./dist

# Define variáveis para o ambiente Python
PYTHON := python3
VENV := .venv
ACTIVATE := source $(VENV)/bin/activate
PYTHON_ENV := PYTHONPATH=.

# Ajuda do Makefile
help:
	@echo "Comandos disponíveis:"
	@echo "  make create-venv              Cria ambiente virtual Python se não existir"
	@echo "  make install                  Instala o projeto no ambiente virtual via pyproject.toml"
	@echo "  make lint                     Executa análise de lint para verificar estilo de código"
	@echo "  make format                   Formata o código usando Black e isort"
	@echo "  make autoflake                Remove imports não utilizados e variáveis não usadas"
	@echo "  make test                     Executa os testes unitários do projeto"
	@echo "  make test-coverage            Executa testes com relatório de cobertura de código"
	@echo "  make cli-test                 Testa a funcionalidade da interface de linha de comando"
	@echo "  make build                    Empacota o projeto usando python -m build"
	@echo "  make clean                    Remove arquivos temporários e de build"
	@echo "  make clean-pycache            Remove apenas arquivos __pycache__ e .pyc"
	@echo "  make clean-cache              Remove arquivos de cache e logs temporários"
	@echo "  make clean-code target=\"dir\" Remove imports/variáveis não utilizados em um diretório"
	@echo "  make all                      Executa lint, test, formatação e atualização de docs"
	@echo ""
	@echo "Agentes disponíveis:"
	@echo ""
	@echo "  make start-github-agent context_id=\"...\"      Inicia o agente de integração com GitHub (GitHubIntegrationAgent)"
	@echo "    Opções: [project_dir=\"...\"] [context_dir=\"...\"] [base_branch=\"...\"] [github_token=\"...\"] [owner=\"...\"] [repo=\"...\"] [model=\"<modelo_openai>\"] [elevation_model=\"<modelo_elevacao>\"] [force=true]"
	@echo "    Exemplo: make start-github-agent context_id=\"feature_concept_20240601_123456\" project_dir=\"/Users/mal/GitHub/agent-flow-craft-aider\" owner=\"Malnati\" repo=\"agent-flow-craft-aider\" model=\"gpt-4-turbo\" elevation_model=\"gpt-4-turbo\""
	@echo "    Tarefas executadas:"
	@echo "      1. Inicializa o GitHubIntegrationAgent com token, owner e repo especificados"
	@echo "      2. Carrega o conceito de feature previamente gerado usando o context_id fornecido"
	@echo "      3. Cria uma nova issue no GitHub com o título e descrição do conceito"
	@echo "      4. Cria uma nova branch no repositório Git local baseada na issue"
	@echo "      5. Cria um arquivo de plano de execução no repositório detalhando a feature"
	@echo "      6. Cria um pull request no GitHub associado à issue e branch"
	@echo "      7. Retorna um JSON com issue_number, branch_name e status da integração"
	@echo ""
	@echo "  make prompt-creator prompt=\"...\"    Inicia o agente coordenador (FeatureCoordinatorAgent)"
	@echo "    Opções: [plan_file=\"...\"] [project_dir=\"...\"] [output=\"...\"] [context_dir=\"...\"] [github_token=\"...\"] [openai_token=\"...\"] [model=\"<modelo_openai>\"] [elevation_model=\"<modelo_elevacao>\"] [force=true]"
	@echo "    Exemplo: make prompt-creator prompt=\"Implementar sistema de notificações\" project_dir=\"/Users/mal/GitHub/agent-flow-craft-aider\" model=\"gpt-4-turbo\" elevation_model=\"gpt-4-turbo\""
	@echo "    Tarefas executadas:"
	@echo "      1. Inicializa o FeatureCoordinatorAgent com tokens e diretórios configurados"
	@echo "      2. Configura o ConceptGenerationAgent interno com o modelo especificado"
	@echo "      3. Obtém o log do Git para contexto da feature"
	@echo "      4. Gera um conceito inicial usando o ConceptGenerationAgent a partir do prompt"
	@echo "      5. Transforma o conceito em feature_concept usando o FeatureConceptAgent"
	@echo "      6. Valida o plano de execução usando o PlanValidator"
	@echo "      7. Processa o conceito no GitHub usando o GitHubIntegrationAgent"
	@echo "      8. Orquestra todo o fluxo entre os diferentes agentes especializados"
	@echo "      9. Retorna um resultado consolidado com todas as informações do processo"
	@echo ""
	@echo "Outros comandos:"
	@echo "  make pack --out=DIRECTORY     Empacota o projeto MCP para o diretório especificado"
	@echo "  make deploy                   Instala a última versão do pacote do PyPI e verifica a instalação"
	@echo "  make publish                  Publica o projeto no PyPI (requer PYPI_KEY)"
	@echo "  make version                  Mostra a versão que será usada na publicação"
	@echo "  make version-info version=X.Y.Z.devN  Mostra informações da versão especificada"
	@echo "  make find-commit version=X.Y.Z.devN   Retorna o hash do commit associado à versão"
	@echo "  make update-changelog version=X.Y.Z.devN  Atualiza o CHANGELOG.md com informações da versão"
	@echo "  make compare-versions from=X.Y.Z.devN to=X.Y.Z.devN  Compara as mudanças entre duas versões"
	@echo ""
	@echo "RefactorAgent: Refatoração de código usando Rope"
	@echo "  make start-refactor-agent project_dir=<diretório_do_projeto> [scope=<arquivo_ou_diretório>] [level=<leve|moderado|agressivo>] [dry_run=true] [output=<arquivo_saída>]"
	@echo "Exemplo:"
	@echo "  make start-refactor-agent project_dir=/caminho/do/projeto scope=src/main.py level=moderado output=resultados.json"

# Verifica se ambiente virtual existe e cria se necessário
create-venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Criando ambiente virtual Python..."; \
		$(PYTHON) -m venv $(VENV); \
		$(ACTIVATE) && $(PYTHON) -m pip install --upgrade pip uv; \
		echo "source $(VENV)/bin/activate" >> $(VENV)/bin/activate; \
	else \
		echo "Ambiente virtual já existe."; \
		$(ACTIVATE) && $(PYTHON) -m pip install -q uv; \
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
	@if [ -z "$(OPENAI_KEY)" ]; then \
		echo "Erro: Variável de ambiente OPENAI_KEY não definida."; \
		exit 1; \
	fi

# Target para iniciar o agente GitHub (GitHubIntegrationAgent)
start-github-agent: check-env create-venv print-no-pycache-message
	@if [ -z "$(context_id)" ]; then \
		echo "Uso: make start-github-agent context_id=\"<id>\" [project_dir=\"<diretório>\"] [context_dir=\"<diretório>\"] [base_branch=\"<branch>\"] [github_token=\"<token>\"] [owner=\"<owner>\"] [repo=\"<repo>\"] [model=\"<modelo_openai>\"] [elevation_model=\"<modelo_elevacao>\"] [force=true]"; \
		exit 1; \
	fi
	@$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src \
		OPENROUTER_KEY="$(OPENROUTER_KEY)" \
		DEEPSEEK_KEY="$(DEEPSEEK_KEY)" \
		GEMINI_KEY="$(GEMINI_KEY)" \
		python -B src/scripts/run_agent_github_integration.py \
		"$(context_id)" \
		$(if $(project_dir),--project_dir "$(project_dir)",) \
		$(if $(context_dir),--context_dir "$(context_dir)",) \
		$(if $(base_branch),--base_branch "$(base_branch)",) \
		$(if $(github_token),--github_token "$(github_token)",) \
		$(if $(owner),--owner "$(owner)",) \
		$(if $(repo),--repo "$(repo)",) \
		$(if $(model),--model "$(model)",) \
		$(if $(elevation_model),--elevation_model "$(elevation_model)",) \
		$(if $(force),--force,) \
		$(ARGS)

# Target para iniciar o agente coordenador (FeatureCoordinatorAgent)
prompt-creator: create-venv print-no-pycache-message
	@if [ -z "$(prompt)" ]; then \
		echo "Uso: make prompt-creator prompt=\"<descricao>\" [project_dir=\"<diretório>\"] [output=\"<arquivo_saida>\"] [context_dir=\"<dir_contexto>\"] [model=\"<modelo_openai>\"] [elevation_model=\"<modelo_elevacao>\"] [force=true]"; \
		exit 1; \
	fi
	@echo "Executando agente coordenador com prompt: \"$(prompt)\""
	@$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python -B src/scripts/run_agent_feature_coordinator.py \
		"$(prompt)" \
		$(if $(project_dir),--target "$(project_dir)",) \
		$(if $(output),--output "$(output)",) \
		$(if $(context_dir),--context_dir "$(context_dir)",) \
		$(if $(github_token),--github_token "$(github_token)",) \
		$(if $(owner),--owner "$(owner)",) \
		$(if $(repo),--repo "$(repo)",) \
		$(if $(openai_token),--openai_token "$(openai_token)",) \
		$(if $(model),--model "$(model)",) \
		$(if $(elevation_model),--elevation_model "$(elevation_model)",) \
		$(if $(force),--force,) \
		$(ARGS)

# Instala as dependências do projeto via uv e pyproject.toml
install: $(VENV)
	@echo "Instalando dependências do projeto via pyproject.toml..."
	@$(ACTIVATE) && $(PYTHON_ENV) uv pip install -e . && uv pip install -e ".[dev]"

# Instala as dependências do projeto em modo de desenvolvimento via pyproject.toml
setup: $(VENV)
	@echo "Instalando dependências de desenvolvimento via pyproject.toml..."
	@$(ACTIVATE) && $(PYTHON_ENV) uv pip install -e ".[dev]"

# Executa todos os testes unitários
test: $(VENV)
	@echo "Executando testes unitários..."
	@$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python -m pytest src/tests -v

# Executa testes com relatório de cobertura
test-coverage: $(VENV)
	@echo "Executando testes com relatório de cobertura..."
	@$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python -m pytest src/tests --cov=src --cov-report=term --cov-report=html
	@echo "✅ Relatório de cobertura HTML gerado em htmlcov/index.html"

# Executa análise de lint para verificar problemas de estilo de código
lint: $(VENV)
	@echo "Executando lint com flake8..."
	@$(ACTIVATE) && $(PYTHON_ENV) flake8 src

# Formata o código usando o Black e isort
format: $(VENV)
	@echo "Formatando código com black e isort..."
	@$(ACTIVATE) && $(PYTHON_ENV) black src tests
	@$(ACTIVATE) && $(PYTHON_ENV) isort src tests
	@$(ACTIVATE) && $(PYTHON_ENV) autoflake --recursive --in-place --remove-all-unused-imports src tests

# Remove imports não utilizados e variáveis não usadas usando autoflake
autoflake: $(VENV)
	@echo "Removendo imports não utilizados e variáveis não usadas com autoflake..."
	@$(ACTIVATE) && $(PYTHON_ENV) autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive src tests

# Empacota o projeto usando python -m build
build: $(VENV)
	@echo "Limpando diretório de distribuição..."
	@rm -rf $(BUILD_DIR)
	@mkdir -p $(BUILD_DIR)
	@echo "Construindo pacote..."
	@$(ACTIVATE) && $(PYTHON_ENV) cd src && python -m build -o ../$(BUILD_DIR)

# Atualiza o índice da documentação automaticamente
update-docs-index: $(VENV)
	@echo "Atualizando índice da documentação..."
	@$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python src/scripts/util_generate_docs_index.py

# Limpa todos os arquivos __pycache__ e .pyc
clean-pycache:
	@echo "Removendo arquivos __pycache__ e .pyc..."
	@$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python src/scripts/util_clean_pycache.py
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@echo "Limpeza de cache Python concluída!"

# Limpa arquivos de cache e logs temporários
clean-cache:
	@echo "Limpando arquivos de cache e logs temporários..."
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".coverage" -exec rm -rf {} +
	@find . -type d -name "htmlcov" -exec rm -rf {} +
	@find logs -type f -name "*.log" -delete
	@echo "Limpeza de cache e logs concluída!"

# Limpa todos os arquivos temporários
clean: clean-pycache clean-cache
	@echo "Limpando arquivos temporários e de build..."
	@find . -type d -name "*.dist-info" -exec rm -rf {} +
	@find . -type d -name "build" -exec rm -rf {} +
	@rm -rf $(BUILD_DIR)/
	@rm -rf *.egg-info/
	@echo "Limpeza completa concluída!"

# Limpa código com autoflake em um diretório específico
clean-code:
	@if [ -z "$(target)" ]; then \
		echo "Uso: make clean-code target=\"<diretório_ou_arquivo>\""; \
		echo "Exemplo: make clean-code target=\"src/\""; \
		exit 1; \
	fi
	@echo "Limpando código no diretório: $(target)"
	@$(ACTIVATE) && $(PYTHON_ENV) autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive "$(target)"
	@echo "✅ Limpeza de código concluída!"

# Executa lint, test, formatação e atualização de docs
all: lint test format autoflake update-docs-index

# Empacotar o projeto
pack:
ifndef out
	$(error Por favor especifique um diretório de saída: make pack out=DIRECTORY)
endif
	@echo "Empacotando projeto na versão $(VERSION)..."
	@mkdir -p $(out)
	@$(ACTIVATE) && $(PYTHON_ENV) python setup.py sdist bdist_wheel
	@cp -f dist/*.whl $(out)/
	@cp -f .cursor/config.json $(out)/ 2>/dev/null || true
	@echo '#!/bin/bash\npip install *.whl\nif [ -f "config.json" ]; then\n  mkdir -p "$(HOME)/.cursor"\n  cp -f config.json "$(HOME)/.cursor/"\n  echo "Configuração instalada!"\nfi\necho "Instalação concluída! Reinicie o Cursor para usar o agent-flow-craft."' > $(out)/install.sh
	@chmod +x $(out)/install.sh
	@echo "Empacotamento concluído! Arquivos disponíveis em: $(out)"

# Implantar o pacote
deploy: $(VENV)
	@echo "\n🚀 Instalando a última versão do pacote agent-flow-craft do PyPI..."
	$(ACTIVATE) && $(PYTHON_ENV) pip install --upgrade --force-reinstall agent-flow-craft
	@echo "\n🔍 Verificando se a instalação foi bem-sucedida..."
	@echo "📦 Versão instalada:"
	@$(ACTIVATE) && $(PYTHON_ENV) pip list | grep -i agent-flow-craft || (echo "❌ Erro: O pacote agent-flow-craft não parece estar instalado." && exit 1)
	@echo "\n⚙️ Verificando importação do pacote..."
	@$(ACTIVATE) && $(PYTHON_ENV) python -c "import importlib.util; spec = importlib.util.find_spec('agent_platform'); print('✅ Pacote importado: ' + spec.origin if spec is not None else '❌ Erro: Não foi possível importar o pacote agent_platform.'); exit(1 if spec is None else 0)"
	@echo "\n✅ Implantação concluída com sucesso!"

# Remover o MCP do Cursor
undeploy:
	@echo "Removendo agent-flow-craft do Cursor IDE..."
	@rm -f $(HOME)/.cursor/agent-flow-craft.json
	@rm -f $(HOME)/.cursor/agent_flow_craft.py
	@rm -rf $(HOME)/.cursor/agent-flow-craft/
	@echo "agent-flow-craft removido com sucesso!"

# Adiciona uma mensagem ao final para lembrar de compilação
print-no-pycache-message:
	@echo "======================================================="
	@echo "LEMBRETE: Arquivos .pyc e diretórios __pycache__ estão desabilitados"
	@echo "Para executar scripts manualmente, prefira usar:"
	@echo "python -B seu_script.py"
	@echo "ou defina a variável de ambiente PYTHONDONTWRITEBYTECODE=1"
	@echo "======================================================="

# Target para iniciar o agente de refatoração Python 
start-refactor-agent: $(VENV) print-no-pycache-message
	@if [ -z "$(project_dir)" ]; then \
		echo "Uso: make start-refactor-agent project_dir=\"<diretório>\" [scope=\"<arquivo_ou_diretório>\"] [level=\"<leve|moderado|agressivo>\"] [dry_run=true] [output=\"<arquivo_saída>\"]"; \
		exit 1; \
	fi
	@echo "Iniciando agente de refatoração Python..."
	@$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python -B src/scripts/run_agent_python_refactor.py \
		--project_dir "$(project_dir)" \
		$(if $(scope),--scope "$(scope)",) \
		$(if $(level),--level "$(level)",) \
		$(if $(dry_run),--dry_run,) \
		$(if $(output),--output "$(output)",) \
		$(ARGS)
	@if [ -z "$(dry_run)" ]; then \
		echo "Executando autoflake para remover imports não utilizados..."; \
		$(ACTIVATE) && $(PYTHON_ENV) autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive "$(project_dir)"; \
		echo "✅ Limpeza de código concluída!"; \
	fi

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
			print(f'Erro: Versão {v} não encontrada em version_commits.json'); \
			exit(1); \
		commit = data[v]['commit_hash']; \
		timestamp = data[v]['timestamp']; \
		if not os.path.exists('CHANGELOG.md'): \
			open('CHANGELOG.md', 'w').write('# Changelog\\n\\n'); \
		content = open('CHANGELOG.md', 'r').read(); \
		if v in content: \
			print(f'Versão {v} já existe no CHANGELOG.md'); \
			exit(0); \
		header = f'## [{v}] - {timestamp.split()[0]}\\n\\n'; \
		cmd = f'git log --pretty=format:\"%s\" {commit}~..{commit}'; \
		log = os.popen(cmd).read().strip(); \
		changes = '\\n'.join([f'- {line}' for line in log.split('\\n') if line.strip()]); \
		if not changes.strip(): \
			changes = '- Atualizações internas'; \
		entry = header + changes + '\\n\\n'; \
		marker = '# Changelog\\n\\n'; \
		new_content = content.replace(marker, marker + entry); \
		open('CHANGELOG.md', 'w').write(new_content); \
		print(f'CHANGELOG.md atualizado com a versão {v}');"

# Comparar mudanças entre duas versões
compare-versions:
	@if [ -z "$(from)" ] || [ -z "$(to)" ]; then \
		echo "Uso: make compare-versions from=X.Y.Z.devN to=X.Y.Z.devN"; \
		exit 1; \
	fi
	@if [ ! -f "version_commits.json" ]; then \
		echo "Erro: Arquivo de mapeamento version_commits.json não encontrado."; \
		exit 1; \
	fi
	@echo "Comparando versões $(from) → $(to) ..."
	@$(PYTHON) -c "import json; import os; import sys; \
		from_v='$(from)'; to_v='$(to)'; \
		data = json.load(open('version_commits.json')); \
		if from_v not in data: \
			print(f'Erro: Versão {from_v} não encontrada em version_commits.json'); \
			sys.exit(1); \
		if to_v not in data: \
			print(f'Erro: Versão {to_v} não encontrada em version_commits.json'); \
			sys.exit(1); \
		from_commit = data[from_v]['commit_hash']; \
		to_commit = data[to_v]['commit_hash']; \
		print(f'\nMudanças entre {from_v} ({from_commit}) e {to_v} ({to_commit}):\n'); \
		os.system(f'git --no-pager log --pretty=format:\"%h - %s (%an)\" {from_commit}..{to_commit}'); \
		print('\n');"

# Mostra a versão atual baseada na data
version:
	@echo "Versão atual: $(VERSION)"

# Mostra informações detalhadas sobre uma versão específica
version-info:
	@if [ -z "$(version)" ]; then \
		echo "Uso: make version-info version=X.Y.Z.devN"; \
		exit 1; \
	fi
	@if [ ! -f "version_commits.json" ]; then \
		echo "Erro: Arquivo de mapeamento version_commits.json não encontrado."; \
		exit 1; \
	fi
	@$(PYTHON) -c "import json; import os; v='$(version)'; \
		data = json.load(open('version_commits.json')); \
		if v not in data: \
			print(f'Erro: Versão {v} não encontrada em version_commits.json'); \
			exit(1); \
		info = data[v]; \
		print(f'\nInformações da versão {v}:'); \
		print(f'Commit: {info["commit_hash"]}'); \
		print(f'Data/Hora: {info["timestamp"]}'); \
		print(f'Build: {info["build_number"]}'); \
		cmd = f'git show --pretty=format:\"%s%n%n%b\" {info["commit_hash"]} --no-patch'; \
		msg = os.popen(cmd).read().strip(); \
		print(f'\nMensagem do commit:\n{msg}\n');"

# Comando para encontrar o hash do commit associado a uma versão
find-commit:
	@if [ -z "$(version)" ]; then \
		echo "Uso: make find-commit version=X.Y.Z.devN"; \
		exit 1; \
	fi
	@if [ ! -f "version_commits.json" ]; then \
		echo "Erro: Arquivo de mapeamento version_commits.json não encontrado."; \
		exit 1; \
	fi
	@$(PYTHON) -c "import json; v='$(version)'; \
		data = json.load(open('version_commits.json')); \
		if v not in data: \
			print(f'Erro: Versão {v} não encontrada em version_commits.json'); \
			exit(1); \
		print(data[v]['commit_hash']);"

# Publicar no PyPI
publish: build
	@if [ -z "$(PYPI_KEY)" ]; then \
		echo "Erro: Variável de ambiente PYPI_KEY não definida."; \
		exit 1; \
	fi
	@echo "Publicando versão $(VERSION) no PyPI..."
	@$(ACTIVATE) && $(PYTHON_ENV) twine upload --non-interactive --repository-url https://upload.pypi.org/legacy/ \
		--username __token__ --password $(PYPI_KEY) \
		$(BUILD_DIR)/*
	@echo "Publicação concluída!"

# Target para testar o CLI da ferramenta
cli-test: $(VENV)
	@echo "Testando a interface de linha de comando..."
	@$(ACTIVATE) && $(PYTHON_ENV) PYTHONPATH=./src python -m src.cli.cli --help 