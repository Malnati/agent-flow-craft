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
├── scripts/
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
4. Crie um script CLI simples (`scripts/start_feature_agent.py`) para facilitar a execução do agente via terminal.

Exemplo de uso do script CLI:

```bash
python scripts/start_feature_agent.py "Descrição da nova funcionalidade" "Plano de execução detalhado"
```

### Estrutura do diretório `docs/pr/`

O diretório `docs/pr/` contém planos de execução detalhados para as issues criadas e pull requests abertos pelo agente de criação de features. Cada arquivo neste diretório segue o formato `<issue_number>_feature_plan.md` e inclui:

- **Prompt recebido:** O prompt original fornecido pelo usuário.
- **Plano de execução gerado pela IA:** Um plano detalhado de como a funcionalidade será implementada, incluindo contexto, descrição da solução, alternativas consideradas, checklist técnico de implementação e observações adicionais.

