.PHONY: install setup test lint format start-agent update-docs-index clean all

# Instala as dependências do projeto via uv
install:
	uv pip install -r requirements.txt
	uv pip install -e .[dev]

# Instala as dependências do projeto em modo de desenvolvimento
setup:
	uv pip install -e .[dev]

# Executa todos os testes unitários
test:
	python -m unittest discover -s tests

# Executa análise de lint para verificar problemas de estilo de código
lint:
	flake8 .

# Formata o código usando o Black
format:
	black .

# Inicia o agente manualmente
start-agent:
	PYTHONPATH=. python scripts/start_feature_agent.py

# Atualiza o índice da documentação automaticamente
update-docs-index:
	PYTHONPATH=. python scripts/generate_docs_index.py

# Limpa todos os arquivos __pycache__
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +

# Executa lint, test, formatação e atualização de docs
all: lint test format update-docs-index