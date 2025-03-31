# Exemplo de Uso do AutoflakeAgent

Este documento demonstra como utilizar o agente de limpeza automática de código AutoflakeAgent para remover imports não utilizados e variáveis não usadas em projetos Python.

## Introdução

O AutoflakeAgent é uma ferramenta que automatiza a limpeza de código Python, removendo:

- Imports não utilizados
- Variáveis não usadas
- Imports com asterisco (expandindo-os)

## Pré-requisitos

- Python 3.7+
- Autoflake instalado: `pip install autoflake`

## Execução via Makefile

O modo mais simples de executar o agente é usando o comando `make`:

```bash
make start-autoflake-agent project_dir=/caminho/do/projeto
```

### Parâmetros adicionais

Você pode personalizar a execução com os seguintes parâmetros:

```bash
make start-autoflake-agent \
  project_dir=/caminho/do/projeto \
  scope=src/modulo \
  aggressiveness=3 \
  dry_run=true \
  output=resultado_limpeza.json
```

## Execução via Linha de Comando

Alternativamente, você pode executar o script diretamente:

```bash
python src/scripts/run_autoflake_agent.py \
  --project_dir /caminho/do/projeto \
  --scope src/modulo \
  --aggressiveness 3 \
  --dry_run \
  --output resultado_limpeza.json
```

## Níveis de Agressividade

O agente suporta três níveis de agressividade:

1. **Leve (1)**: Remove apenas imports não utilizados
2. **Moderado (2)**: Remove imports não utilizados e variáveis não usadas
3. **Agressivo (3)**: Remove imports não utilizados, variáveis não usadas e expande imports com asterisco

## Modo Dry-Run

Para visualizar quais alterações seriam feitas sem aplicá-las, utilize o modo dry-run:

```bash
make start-autoflake-agent project_dir=/caminho/do/projeto dry_run=true
```

## Exemplos de Saída

O agente gera um arquivo JSON de saída com o resultado da limpeza. Exemplo:

```json
{
  "status": "success",
  "dry_run": false,
  "aggressiveness": 2,
  "command": "autoflake --recursive --remove-all-unused-imports --remove-unused-variables --in-place --exclude venv/ --exclude .venv/ --exclude __pycache__/ --exclude dist/ --exclude build/ --exclude tests/ --exclude .git/ --exclude .pytest_cache/ --exclude .mypy_cache/ --exclude *.egg-info/ --exclude *.egg/ /caminho/do/projeto/src",
  "statistics": {
    "files_analyzed": 42,
    "files_modified": 15,
    "lines_removed": 87,
    "errors": 0,
    "warnings": 0,
    "duration_seconds": 1.25
  },
  "modified_files": [
    "/caminho/do/projeto/src/modulo/arquivo1.py",
    "/caminho/do/projeto/src/modulo/arquivo2.py"
  ],
  "file_changes": {
    "/caminho/do/projeto/src/modulo/arquivo1.py": {
      "before": 120,
      "after": 115,
      "removed": 5
    },
    "/caminho/do/projeto/src/modulo/arquivo2.py": {
      "before": 87,
      "after": 83,
      "removed": 4
    }
  }
}
```

## Integração com CI/CD

O agente pode ser integrado em pipelines de CI/CD para garantir que o código esteja sempre limpo. Exemplo para GitHub Actions:

```yaml
name: Python Code Cleanup

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install autoflake
        pip install -r requirements.txt
    - name: Run AutoflakeAgent (dry-run)
      run: |
        python src/scripts/run_autoflake_agent.py --project_dir . --aggressiveness 2 --dry_run --output autoflake_result.json
    - name: Upload result
      uses: actions/upload-artifact@v3
      with:
        name: autoflake-result
        path: autoflake_result.json
``` 