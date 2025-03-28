.PHONY: install setup test lint format start-agent update-docs-index clean all create-venv

# Define variáveis para o ambiente Python
VENV_DIR := .venv
PYTHON := python3
ACTIVATE := . $(VENV_DIR)/bin/activate

# Verifica se ambiente virtual existe e cria se necessário
create-venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Criando ambiente virtual Python..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
		$(ACTIVATE) && pip install --upgrade pip; \
		$(ACTIVATE) && pip install pyyaml requests click pyautogen openai python-slugify; \
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
	$(ACTIVATE) && uv pip install -e . && uv pip install -e .[dev]

# Instala as dependências do projeto em modo de desenvolvimento
setup: create-venv
	$(ACTIVATE) && uv pip install -e .[dev]

# Executa todos os testes unitários
test: create-venv
	$(ACTIVATE) && python -m unittest discover -s tests

# Executa análise de lint para verificar problemas de estilo de código
lint: create-venv
	$(ACTIVATE) && flake8 .

# Formata o código usando o Black
format: create-venv
	$(ACTIVATE) && black .

# Exemplo de uso:
# make start-agent prompt="Descrição da feature" execution_plan="Plano detalhado de execução"
start-agent: check-env create-venv
	@if [ -z "$(prompt)" ] || [ -z "$(execution_plan)" ]; then \
		echo "Uso: make start-agent prompt=\"<descricao>\" execution_plan=\"<plano de execucao>\""; \
		exit 1; \
	fi
	$(ACTIVATE) && PYTHONPATH=. python scripts/start_feature_agent.py "$(prompt)" "$(execution_plan)" --token "$(GITHUB_TOKEN)" --owner "$(GITHUB_OWNER)" --repo "$(GITHUB_REPO)" --openai_token "$(OPENAI_TOKEN)"

# Atualiza o índice da documentação automaticamente
update-docs-index: create-venv
	$(ACTIVATE) && PYTHONPATH=. python scripts/generate_docs_index.py

# Limpa todos os arquivos __pycache__
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +

# Executa lint, test, formatação e atualização de docs
all: lint test format update-docs-index