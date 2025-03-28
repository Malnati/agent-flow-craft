# AgentFlowCraft

> Estrutura automatizada para criação, execução, avaliação e conformidade de múltiplos agentes de IA orientados a microtarefas, com registro e rastreamento completo.

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
# Configurar token do PyPI
export PyPI_TOKEN=seu_token_aqui

# Publicar no PyPI
make publish
```

Para publicar o pacote, você precisa:
1. Ter uma conta ativa no PyPI (https://pypi.org)
2. Criar uma chave de API em https://pypi.org/manage/account/token/
3. Definir a variável de ambiente `PyPI_TOKEN` com sua chave
4. Executar o comando `make publish`

O comando verificará a presença do token, construirá o pacote e fará o upload para o PyPI automaticamente.

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
