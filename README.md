# AgentFlowCraft

> Estrutura automatizada para criação, execução, avaliação e conformidade de múltiplos agentes de IA orientados a microtarefas, com registro e rastreamento completo.

---

## 📦 Instalação

Você pode instalar o AgentFlowCraft diretamente via pip:

```bash
# Instalar a versão mais recente do PyPI
pip install agent-flow-craft

# Ou instalar a versão de desenvolvimento diretamente do GitHub
pip install git+https://github.com/Malnati/agent-flow-craft.git
```

Para desenvolvimento local, recomendamos clonar o repositório:

```bash
# Clonar o repositório
git clone https://github.com/Malnati/agent-flow-craft.git
cd agent-flow-craft

# Instalar em modo de desenvolvimento
pip install -e .
```

Após a instalação, certifique-se de configurar as variáveis de ambiente necessárias:

```bash
# Para integração com GitHub
export GITHUB_TOKEN=seu_token_aqui
export GITHUB_OWNER=seu_usuario_github
export GITHUB_REPO=nome_do_repositorio

# Para uso da API OpenAI
export OPENAI_API_KEY=seu_token_openai
```

---

## 📋 Comandos do Makefile

O projeto disponibiliza diversos comandos através do Makefile para facilitar o uso dos agentes e a execução de tarefas comuns.

### Comandos de desenvolvimento

```bash
make create-venv              # Cria ambiente virtual Python se não existir
make install                  # Instala o projeto no ambiente virtual
make setup                    # Instala o projeto em modo de desenvolvimento
make test                     # Executa os testes do projeto
make lint                     # Executa análise de lint para verificar estilo de código
make format                   # Formata o código usando o Black
make build                    # Empacota o projeto usando python -m build
make clean                    # Remove arquivos temporários e de build
make clean-pycache            # Remove apenas os diretórios __pycache__ e arquivos .pyc
make all                      # Executa lint, test, formatação e atualização de docs
make update-docs-index        # Atualiza o índice da documentação automaticamente
```

### Agentes disponíveis

#### 1. Agente de criação de features (FeatureCoordinatorAgent)
```bash
make start-agent prompt="<descricao>" project_dir="<diretório>" [model="<modelo_openai>"]
```
**Exemplo:** `make start-agent prompt="Implementar sistema de login" project_dir="/Users/mal/GitHub/agent-flow-craft-aider" model="gpt-4-turbo"`

**Tarefas executadas:**
1. Inicializa o FeatureCoordinatorAgent com os parâmetros fornecidos
2. Configura o modelo OpenAI especificado no ConceptGenerationAgent interno
3. Cria um diretório de contexto para armazenar os resultados
4. Gera um conceito de feature a partir do prompt usando a API OpenAI
5. Processa a criação da feature com base no conceito gerado
6. Retorna o resultado em JSON com informações da feature criada

#### 2. Agente de geração de conceitos (ConceptGenerationAgent)
```bash
make start-concept-agent prompt="<descricao>" [output="<arquivo_saida>"] [context_dir="<dir_contexto>"] [project_dir="<dir_projeto>"] [model="<modelo_openai>"]
```
**Exemplo:** `make start-concept-agent prompt="Adicionar autenticação via OAuth" project_dir="/Users/mal/GitHub/agent-flow-craft-aider" context_dir="agent_context"`

**Tarefas executadas:**
1. Inicializa o ConceptGenerationAgent com o token OpenAI e modelo especificados
2. Obtém o log do Git do projeto (se disponível) para fornecer contexto
3. Envia o prompt e contexto para a API OpenAI para gerar um conceito de feature
4. Estrutura a resposta em JSON com branch_type, issue_title, issue_description, etc.
5. Salva o conceito gerado no diretório de contexto com um ID único
6. Retorna o conceito completo com o context_id para uso posterior

#### 3. Agente de integração com GitHub (GitHubIntegrationAgent)
```bash
make start-github-agent context_id="<id>" [project_dir="<diretório>"] [context_dir="<diretório>"] [base_branch="<branch>"] [github_token="<token>"] [owner="<owner>"] [repo="<repo>"]
```
**Exemplo:** `make start-github-agent context_id="feature_concept_20240601_123456" project_dir="/Users/mal/GitHub/agent-flow-craft-aider" owner="Malnati" repo="agent-flow-craft-aider"`

**Tarefas executadas:**
1. Inicializa o GitHubIntegrationAgent com token, owner e repo especificados
2. Carrega o conceito de feature previamente gerado usando o context_id fornecido
3. Cria uma nova issue no GitHub com o título e descrição do conceito
4. Cria uma nova branch no repositório Git local baseada na issue
5. Cria um arquivo de plano de execução no repositório detalhando a feature
6. Cria um pull request no GitHub associado à issue e branch
7. Retorna um JSON com issue_number, branch_name e status da integração

#### 4. Agente coordenador (FeatureCoordinatorAgent)
```bash
make start-coordinator-agent prompt="<descricao>" [project_dir="<diretório>"] [plan_file="<arquivo>"] [output="<arquivo>"] [context_dir="<diretório>"] [github_token="<token>"] [openai_token="<token>"] [model="<modelo_openai>"]
```
**Exemplo:** `make start-coordinator-agent prompt="Implementar sistema de notificações" project_dir="/Users/mal/GitHub/agent-flow-craft-aider" model="gpt-4-turbo"`

**Tarefas executadas:**
1. Inicializa o FeatureCoordinatorAgent com tokens e diretórios configurados
2. Configura o ConceptGenerationAgent interno com o modelo especificado
3. Obtém o log do Git para contexto da feature
4. Gera um conceito usando o ConceptGenerationAgent a partir do prompt
5. Salva o conceito no sistema de gerenciamento de contexto
6. Valida o plano de execução usando o PlanValidator
7. Processa o conceito no GitHub usando o GitHubIntegrationAgent
8. Orquestra todo o fluxo entre os diferentes agentes especializados
9. Retorna um resultado consolidado com todas as informações do processo

#### 5. Gerenciador de contexto (ContextManager)
```bash
make start-context-manager operation="<lista|obter|criar|atualizar|excluir>" [context_id="<id>"] [data_file="<arquivo.json>"] [limit=10] [type="<tipo>"] [context_dir="<dir_contexto>"] [output="<arquivo>"]
```
**Exemplo:** `make start-context-manager operation="listar" context_dir="agent_context" limit=5`

**Tarefas executadas:**
1. Inicializa o ContextManager com o diretório de contexto especificado
2. Baseado na operação solicitada, executa uma das seguintes ações:
   - lista: Lista os contextos disponíveis com limite e filtro por tipo
   - obter: Recupera um contexto específico pelo ID
   - criar: Cria um novo contexto a partir de um arquivo JSON
   - atualizar: Atualiza um contexto existente com novos dados
   - excluir: Remove um contexto pelo ID
   - limpar: Remove contextos antigos com base em dias especificados
3. Formata e exibe o resultado da operação solicitada
4. Opcionalmente salva o resultado em um arquivo de saída

#### 6. Validador de planos (PlanValidator)
```bash
make start-validator plan_file="<arquivo_plano.json>" [output="<arquivo_saida>"] [requirements="<arquivo_requisitos>"] [context_dir="<dir_contexto>"] [project_dir="<dir_projeto>"] [model="<modelo_openai>"]
```
**Exemplo:** `make start-validator plan_file="planos/feature_plan.json" project_dir="/Users/mal/GitHub/agent-flow-craft-aider" model="gpt-4-turbo"`

**Tarefas executadas:**
1. Inicializa o PlanValidator com as configurações fornecidas
2. Carrega o plano de execução do arquivo JSON especificado
3. Carrega os requisitos específicos de validação (se fornecidos)
4. Usa a API OpenAI para analisar o plano contra os requisitos
5. Avalia a qualidade e completude do plano de execução
6. Identifica potenciais problemas e sugestões de melhoria
7. Atribui uma pontuação de validação ao plano (de 0 a 10)
8. Retorna um relatório detalhado com o resultado da validação

---

## ✅ Status do projeto

[![Verificação de Assets](https://github.com/Malnati/agent-flow-craft/actions/workflows/check-assets.yml/badge.svg)](https://github.com/Malnati/agent-flow-craft/actions/workflows/check-assets.yml)
[![Lint Python](https://github.com/Malnati/agent-flow-craft/actions/workflows/lint-python.yml/badge.svg)](https://github.com/Malnati/agent-flow-craft/actions/workflows/lint-python.yml)
[![Verificação de Markdown](https://github.com/Malnati/agent-flow-craft/actions/workflows/check-markdown.yml/badge.svg)](https://github.com/Malnati/agent-flow-craft/actions/workflows/check-markdown.yml)
[![Validação de YAML](https://github.com/Malnati/agent-flow-craft/actions/workflows/check-yaml.yml/badge.svg)](https://github.com/Malnati/agent-flow-craft/actions/workflows/check-yaml.yml)
[![Atualização do TREE.md](https://github.com/Malnati/agent-flow-craft/actions/workflows/update-tree.yml/badge.svg)](https://github.com/Malnati/agent-flow-craft/actions/workflows/update3.yml)
[![Auto Tagging](https://github.com/Malnati/agent-flow-craft/actions/workflows/auto-tag.yml/badge.svg)](https://github.com/Malnati/agent-flow-craft/actions/workflows/auto-tag.yml)
[![Atualizar índice da documentação](https://github.com/Malnati/agent-flow-craft/actions/workflows/update-docs-index.yml/badge.svg)](https://github.com/Malnati/agent-flow-craft/actions/workflows/update-docs-index.yml)
[![Changelog](https://img.shields.io/badge/changelog-visualizar-blue)](CHANGELOG.md)

---

## 📚 Contextualização do Projeto
Este repositório nasce de uma análise comparativa das principais ferramentas de desenvolvimento de agentes de IA (LangChain, LangFlow, AutoGen, CrewAI e Agno), avaliando popularidade, comunidade ativa e frequência de commits.

O objetivo principal é criar agentes de IA para execução autônoma de microtarefas, automatizando fluxos e utilizando inteligência artificial para replicar e acelerar o trabalho humano.

---

## 🚀 Tecnologias consideradas para o projeto
Abaixo, a lista de ferramentas consideradas durante a análise para compor o ecossistema deste projeto:

| Ferramenta      | Motivo de consideração                                     |
|-----------------|------------------------------------------------------------|
| **LangChain**   | Popularidade, comunidade ativa e frequência alta de commits. |
| **LangFlow**    | Interface visual para composição de fluxos de agentes.     |
| **AutoGen (MS)**| Robustez, confiabilidade e forte suporte institucional.    |
| **Agno (ex-Phidata)** | Flexibilidade para construção de agentes customizados.|
| **CrewAI**      | Colaboração entre múltiplos agentes com orquestração.     |
| **UV**          | Gerenciador de ambientes Python ágil e eficiente.         |
| **Cursor IDE**  | Ambiente de desenvolvimento altamente produtivo.          |
| **Aider**       | Assistente IA para desenvolvimento contextualizado.       |

### 📊 Comparativo de Popularidade e Atividade (dados coletados em 24 de março de 2025)

| Ferramenta      | Estrelas (⭐) | Contribuidores | Commits/Semana (últimos 6 meses) |
|-----------------|--------------|----------------|----------------------------------|
| **LangChain**   | ~104.000     | 3.529          | ~75                              |
| **LangFlow**    | ~52.800      | 262            | ~85                              |
| **AutoGen (MS)**| ~42.100      | 483            | ~80                              |
| **CrewAI**      | ~29.000      | 229            | ~30                              |
| **Agno**        | ~21.800      | 139            | ~40                              |

> **Conclusão**: O **LangChain** é a ferramenta mais popular e ativa, com grande comunidade. O **AutoGen** da Microsoft destaca-se pela confiabilidade e suporte contínuo. No momento, a tendência é utilizar o **AutoGen**, pela tradição da Microsoft em manter ferramentas bem documentadas e com suporte duradouro, mas o LangChain permanece como forte alternativa.

---

## 🛠 Estrutura dos agentes
Cada agente conterá:
- Registro do prompt inicial.
- Linha de raciocínio da IA (quando suportado pelo modelo).
- Log detalhado da execução.
- Arquivo `conformities.yaml` com parâmetros de conformidade.
- Avaliador automático de conformidade.
- Executor de ajustes automáticos.
- Mecanismo de fallback para intervenção manual.

---

## 📂 Estrutura planejada do repositório
```
agent-flow-craft/
│
├── docs/
├── agents/
├── templates/
├── evaluators/
├── logs/
├── examples/
├── config/
├── .github/
├── README.md
├── CONTRIBUTING.md
├── LICENSE
└── roadmap.md
```
> A estrutura acima é gerada e mantida automaticamente no arquivo [TREE.md](./TREE.md).

---

## 🗺 Roadmap
Consulte o [roadmap completo](./roadmap.md) para ver as etapas em andamento, próximas metas e o ciclo de releases.

---

## 📸 Demonstrações visuais

### ✅ Ciclo de vida do agente
![Ciclo de Vida do Agente](docs/assets/ciclo-agente.png)

### ✅ Estrutura de pastas do projeto
![Estrutura de Pastas](docs/assets/estrutura-pastas.png)

### ✅ Execução simulada de um agente em terminal
![Execução do Agente](docs/assets/execucao-terminal.png)

### ✅ Ciclo de avaliação e feedback do agente
![Ciclo de Feedback do Avaliador](docs/assets/ciclo-feedback.png)

---

## 🧩 Templates disponíveis

O projeto oferece templates prontos para:
- Relato de bugs: [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md)
- Sugestões de novas funcionalidades: [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md)
- Pull Requests: [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md)

## 📂 Documentação interna

- [📚 Documentação principal (docs/README.md)](docs/README.md)
- O diretório `docs/pr/` contém os planos de execução gerados automaticamente a cada PR criado pelos agentes.
- O índice dos planos de execução é atualizado automaticamente via workflow do GitHub Actions.
- A estrutura do projeto é mantida atualizada no arquivo [TREE.md](./TREE.md).

---

## 🌐 Comunidade e Recursos

[![Contribua!](https://img.shields.io/badge/contribua-%F0%9F%91%8D-blue)](./CONTRIBUTING.md)
[![Código de Conduta](https://img.shields.io/badge/c%C3%B3digo%20de%20conduta-respeite%20as%20regras-orange)](./CODE_OF_CONDUCT.md)
[![Roadmap](https://img.shields.io/badge/roadmap-planejamento-green)](./roadmap.md)
[![Suporte](https://img.shields.io/badge/suporte-ajuda-important)](./SUPPORT.md)
[![Relatar problema](https://img.shields.io/badge/issues-reportar%20problema-lightgrey)](../../issues)

---

## 🛡 Segurança

Para detalhes sobre como relatar vulnerabilidades, consulte o nosso [SECURITY.md](./SECURITY.md).

---

## 💡 Contribua com a comunidade
Se você gosta do projeto, ⭐ favorite o repositório, compartilhe com colegas e participe das discussões e melhorias!

---

## 📣 Divulgação e engajamento

- Use a hashtag **#AgentFlowCraft** no Twitter e LinkedIn.
- Participe das discussões (em breve) na aba Discussions do GitHub.
- Acompanhe atualizações e releases pelo [roadmap](./roadmap.md).

---

## 📅 Última atualização deste README
*Última atualização: 26 de março de 2025*

---

## 🛠️ Automação da criação de features

### FeatureCreationAgent

O `FeatureCreationAgent` é um agente responsável por automatizar o fluxo de criação de novas funcionalidades no repositório. Ele realiza as seguintes etapas:

1. Recebe um prompt do usuário descrevendo a funcionalidade desejada.
2. Cria uma issue no GitHub com base no prompt.
3. Cria uma branch vinculada à issue.
4. Gera um plano de execução detalhado e salva no diretório `docs/pr/`.
5. Faz commit e push do plano de execução.
6. Abre um Pull Request vinculado à issue criada.

### Uso

Para utilizar o `FeatureCreationAgent`, siga os passos abaixo:

1. Certifique-se de que o ambiente Python está configurado e que o GitHub CLI (`gh`) está instalado e autenticado.
2. Instale a dependência `pyautogen` utilizando `uv pip install pyautogen`.
3. Adicione a dependência no arquivo de controle (`requirements.txt` ou `pyproject.toml`).
4. Crie um script CLI simples (`src/scripts/start_feature_agent.py`) para facilitar a execução do agente via terminal.

Exemplo de uso do script CLI:

```bash
python src/scripts/start_feature_agent.py "Descrição da nova funcionalidade" "Plano de execução detalhado"
```

### Publicação no PyPI

O projeto inclui um comando para publicação automatizada no Python Package Index (PyPI):

```bash
# Verificar a versão que será publicada
make version

# Configurar token do PyPI
export PyPI_TOKEN=seu_token_aqui

# Publicar no PyPI
make publish

# Para definir uma versão específica (padrão Semantic Versioning)
VERSION=1.2.3 make publish
```

Para publicar o pacote, você precisa:
1. Ter uma conta ativa no PyPI (https://pypi.org)
2. Criar uma chave de API em https://pypi.org/manage/account/token/
3. Definir a variável de ambiente `PyPI_TOKEN` com sua chave
4. Executar o comando `make publish`

#### Sistema de Versionamento

O sistema de versionamento segue o padrão PEP 440 (compatível com PyPI), com a seguinte estrutura:

```
MAJOR.MINOR.PATCH.devN
```

Onde:
- **MAJOR.MINOR**: Ano e mês (ex: 2025.03)
- **PATCH**: Dia do mês (ex: 28)
- **N**: Número único derivado do timestamp e hash do commit (ex: 10150123)

Exemplos:
- Versão automática: `2025.03.28.dev10150123`
- Versão manual: `1.2.3.dev10150123` (quando definida via `VERSION=1.2.3 make publish`)

Este formato garante que:
1. Cada publicação tem uma versão única (evitando o erro "File already exists")
2. As versões são 100% compatíveis com o PyPI (seguindo estritamente o PEP 440)
3. O sistema mantém rastreabilidade através do arquivo `version_commits.json`

#### Rastreabilidade de Versões para Commits

O projeto mantém um registro das associações entre versões publicadas e commits no arquivo `version_commits.json`. Isso permite identificar exatamente qual código-fonte corresponde a cada versão publicada.

Para consultar estas informações, use os comandos:

```bash
# Ver informações completas de uma versão
make version-info version=2025.3.28.dev10150123

# Obter apenas o hash do commit de uma versão (útil para scripts)
make find-commit version=2025.3.28.dev10150123

# Atualizar o CHANGELOG.md com informações da versão
make update-changelog version=2025.3.28.dev10150123

# Comparar mudanças entre duas versões
make compare-versions from=2025.3.28.dev1020023 to=2025.3.28.dev1020131
```

#### Integração com CHANGELOG

O sistema atualiza automaticamente o arquivo `CHANGELOG.md` após cada publicação, registrando:
- A versão publicada
- A data de publicação
- O commit exato associado à versão
- A mensagem do commit

Isso permite manter um histórico completo e rastreável de todas as versões publicadas. A atualização é feita automaticamente pelo comando `make publish`, mas também pode ser realizada manualmente com `make update-changelog`.

#### Ferramentas de Análise de Versões

O comando `compare-versions` permite visualizar facilmente as diferenças entre duas versões publicadas:
- Lista todos os commits entre as duas versões
- Fornece o comando git para ver as diferenças exatas de código
- Mostra informações de data e hora para cada versão

Estas ferramentas são especialmente úteis para:
- Localizar exatamente qual versão introduziu uma determinada funcionalidade ou bug
- Preparar notas de lançamento detalhadas
- Rastrear a evolução do código entre diferentes versões publicadas
- Identificar regressões entre versões

### Estrutura do diretório `docs/pr/`

O diretório `docs/pr/` contém planos de execução detalhados para as issues criadas e pull requests abertos pelo agente de criação de features. Cada arquivo neste diretório segue o formato `<issue_number>_feature_plan.md` e inclui:

- **Prompt recebido:** O prompt original fornecido pelo usuário.
- **Plano de execução gerado pela IA:** Um plano detalhado com informações estruturadas sobre a implementação da feature.

#### Estrutura do Plano de Execução

Cada plano de execução contém uma ou mais entregáveis, e para cada entregável são detalhados:

1. **Nome e Descrição:** Identificação clara e descrição detalhada do propósito do entregável.
2. **Dependências:** Lista completa de dependências técnicas (bibliotecas, serviços, etc.) necessárias.
3. **Exemplo de Uso:** Exemplo prático, geralmente com código, de como o entregável será utilizado.
4. **Critérios de Aceitação:** Lista objetiva e mensurável de critérios para validar o entregável.
5. **Resolução de Problemas:** Possíveis problemas que podem ocorrer, suas causas e resoluções.
6. **Passos de Implementação:** Lista sequencial e detalhada de passos para implementar o entregável.

Exemplo de um entregável em um plano de execução:

```markdown
### Entregável 1: Gerador de Plano de Execução

**Descrição:** Módulo responsável por gerar planos de execução detalhados a partir do prompt do usuário e do contexto do projeto.

**Dependências:**
- pyautogen>=0.2.0
- openai>=1.0.0
- gitpython>=3.1.30

**Exemplo de uso:**
```python
# Cria um gerador de plano
gerador = GeradorPlanoExecucao(openai_token="sk-xxx")

# Gera o plano a partir do prompt e contexto
plano = gerador.gerar_plano(
    prompt="Implementar sistema de autenticação",
    contexto_projeto=obter_contexto_projeto()
)

# Salva o plano em um arquivo
plano.salvar("docs/pr/42_feature_plan.md")
```

**Critérios de aceitação:**
- O plano gerado deve incluir todos os elementos obrigatórios (nome, descrição, dependências, etc.)
- O plano deve ser específico ao contexto do projeto
- O plano deve ser gerado em menos de 30 segundos
- O formato do plano deve seguir o padrão Markdown definido

**Resolução de problemas:**
- Problema: API da OpenAI retorna erro
  - Causa possível: Token inválido ou expirado
  - Resolução: Verificar e renovar o token de acesso

**Passos de implementação:**
1. Criar a classe GeradorPlanoExecucao
2. Implementar método para obter contexto do projeto (arquivos, histórico git)
3. Implementar integração com a API da OpenAI
4. Desenvolver prompt template para gerar o plano
5. Implementar parser para converter a resposta da API em estrutura de dados
6. Criar método para exportar o plano em formato Markdown
7. Implementar tratamento de erros e retentativas
```

Este formato estruturado ajuda a garantir que todos os planos de execução tenham informações completas e úteis para a implementação.

---

## 🛠️ Comandos disponíveis via Makefile

Para facilitar a execução de tarefas comuns no projeto, utilize os comandos abaixo:

| Comando                | Descrição                                                               |
|------------------------|-------------------------------------------------------------------------|
| `make install`         | Instala todas as dependências via `uv` utilizando o `pyproject.toml`.   |
| `make lint`            | Executa verificação de lint nos arquivos Python.                        |
| `make test`            | Executa todos os testes unitários.                                      |
| `make update-tree`     | Atualiza automaticamente o arquivo `TREE.md`.                           |
| `make update-docs`     | Atualiza o índice de documentação dentro da pasta `docs/`.              |
| `make tag`             | Executa o workflow de auto tagging conforme convenção semântica.        |
| `make check-assets`    | Valida a presença dos assets obrigatórios nas pastas de documentação.   |
| `make all`             | Executa lint, testes e atualizações em sequência.                       |
| `make start-agent`     | Inicia o agente de criação de features com ambiente Python configurado. |
| `make create-venv`     | Cria um ambiente virtual Python para o projeto.                         |

> Para usar, basta rodar:  
> ```bash
> # Exemplo: Inicia o agente de criação de features
> make start-agent prompt="Descrição da feature" execution_plan="Plano detalhado"
> 
> # Os comandos gerenciam automaticamente o ambiente virtual Python
> ```

# Agent Flow Craft

Agent Flow Craft é uma plataforma para orquestração de agentes especializados que trabalham juntos para criar features em projetos de software.

## Funcionalidades

- Geração de conceitos de features baseados em prompts do usuário
- Validação de planos de execução
- Criação automática de issues, branches e PRs no GitHub
- Sistema de contexto para transferência de dados entre agentes
- Agentes especializados e autônomos que podem trabalhar juntos ou separadamente

## Arquitetura

O sistema é composto por vários agentes especializados:

1. **ConceptGenerationAgent**: Gera conceitos de features a partir de prompts do usuário usando a OpenAI
2. **PlanValidator**: Valida planos de execução de features
3. **GitHubIntegrationAgent**: Integra com o GitHub para criar issues, branches e PRs
4. **ContextManager**: Gerencia a transferência de dados entre agentes
5. **FeatureCoordinatorAgent**: Coordena o fluxo de trabalho entre os agentes especializados

## Instalação

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/agent-flow-craft.git
cd agent-flow-craft

# Instalar o projeto
make install
```

## Configuração

Configure as variáveis de ambiente necessárias:

```bash
# Credenciais GitHub
export GITHUB_TOKEN=seu_token_github
export GITHUB_OWNER=seu_usuario_github
export GITHUB_REPO=nome_do_repositorio

# Credenciais OpenAI
export OPENAI_API_KEY=seu_token_openai
```

## Uso

### Agente Coordenador (Fluxo Completo)

Para executar o fluxo completo de criação de feature:

```bash
make start-coordinator-agent prompt="Implementar sistema de login com autenticação de dois fatores" \
  target="/caminho/para/repositorio" \
  output="resultado.json"
```

Opcionalmente, você pode fornecer um arquivo de plano:

```bash
make start-coordinator-agent prompt="Implementar sistema de login com autenticação de dois fatores" \
  plan_file="plano.json" \
  target="/caminho/para/repositorio"
```

### Agentes Individuais

Você pode executar cada agente especializado de forma autônoma:

#### Agente de Geração de Conceitos

```bash
make start-concept-agent prompt="Implementar sistema de login com autenticação de dois fatores" \
  output="conceito.json"
```

#### Agente de Integração GitHub

```bash
make start-github-agent context_id="feature_concept_20240328_123456" \
  target="/caminho/para/repositorio"
```

#### Gerenciador de Contexto

```bash
# Listar contextos
make start-context-manager operation=lista limit=5 type="feature_concept"

# Obter um contexto específico
make start-context-manager operation=obter context_id="feature_concept_20240328_123456"

# Criar um novo contexto
make start-context-manager operation=criar data_file="dados.json" type="feature_concept"

# Atualizar um contexto
make start-context-manager operation=atualizar context_id="feature_concept_20240328_123456" \
  data_file="novos_dados.json" merge=true

# Excluir um contexto
make start-context-manager operation=excluir context_id="feature_concept_20240328_123456"

# Limpar contextos antigos
make start-context-manager operation=limpar days=30
```

#### Validador de Planos

```bash
make start-validator plan_file="plano.json" output="validacao.json"
```

## Fluxo de Trabalho

O fluxo completo usando o FeatureCoordinatorAgent segue estas etapas:

1. Geração de conceito a partir do prompt do usuário (ConceptGenerationAgent)
2. Validação e correção do plano de execução (PlanValidator)
3. Criação de issue, branch e PR no GitHub (GitHubIntegrationAgent)
4. Transferência de dados entre as etapas usando contextos (ContextManager)

Os desenvolvedores podem intervir em qualquer ponto do processo, usando os agentes individuais para modificar ou complementar partes específicas do fluxo.

## Contribuição

Contribuições são bem-vindas! Por favor, siga estas etapas:

1. Fork o projeto
2. Crie sua branch de feature (`git checkout -b feature/amazing-feature`)
3. Faça commit das suas mudanças (`git commit -m 'Add some amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.
