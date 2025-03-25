# AgentFlowCraft

> Estrutura automatizada para criação, execução, avaliação e conformidade de múltiplos agentes de IA orientados a microtarefas, com registro e rastreamento completo.

---

## 📚 Contextualização do Projeto
Este repositório nasce de uma análise comparativa das principais ferramentas de desenvolvimento de agentes de IA (LangChain, LangFlow, AutoGen, CrewAI e Agno), avaliando popularidade, comunidade ativa e frequência de commits.

O objetivo principal é criar agentes de IA para execução autônoma de microtarefas, automatizando fluxos e utilizando a inteligência artificial para replicar e acelerar o trabalho humano.

---

## 🎯 Objetivos Principais
- Criar agentes de IA para microtarefas com estrutura padronizada.
- Registrar o prompt inicial e a linha de raciocínio (quando o modelo permitir).
- Manter logs de execução completos (entrada → resposta → ações tomadas).
- Avaliar automaticamente a conformidade de cada resposta com critérios pré-definidos.
- Permitir retrabalho automatizado em loop até 100% de conformidade ou intervenção manual.

---

## 🛠 Estrutura dos Agentes
Cada agente conterá:
- Prompt inicial salvo.
- Linha de raciocínio da IA (se disponível).
- Log estruturado da execução.
- Arquivo `conformities.yaml` com parâmetros de conformidade.
- Avaliador automático para identificar não-conformidades.
- Executor de ajustes com base nas não-conformidades.
- Fallback para intervenção manual se houver bloqueios.

---

## 🚀 Tecnologias consideradas para o projeto
Abaixo, a lista de ferramentas consideradas durante a análise para compor o ecossistema deste projeto:

| Ferramenta      | Motivo da escolha                                     |
|-----------------|-------------------------------------------------------|
| **LangChain**   | Comunidade enorme e altíssima frequência de commits.  |
| **LangFlow**    | Interface visual para composição rápida de fluxos.    |
| **AutoGen (MS)**| Robusto, confiável, ótimo para agentes coordenados.   |
| **Agno**        | Flexível e adaptável, excelente para prototipação.    |
| **CrewAI**      | Orientado a colaboração entre múltiplos agentes.      |
| **UV**          | Gerenciador de ambientes Python rápido e prático.     |

**Decisões atuais**: já está definido o uso do **UV**, do **Cursor** como IDE e do **Aider** para o fluxo de desenvolvimento assistido. As demais ferramentas ainda estão em avaliação, com forte tendência de escolha pelo **LangChain** ou pelo **Microsoft AutoGen**, a depender de testes adicionais.

📊 Comparativo de Popularidade e Atividade (dados coletados em 24 de março de 2025)

| Ferramenta      | Estrelas (⭐) | Contribuidores | Commits/Semana (últimos 6 meses) |
|-----------------|--------------|----------------|----------------------------------|
| **LangChain**   | ~104.000     | 3.529          | ~75                              |
| **LangFlow**    | ~52.800      | 262            | ~85                              |
| **AutoGen (MS)**| ~42.100      | 483            | ~80                              |
| **CrewAI**      | ~29.000      | 229            | ~30                              |
| **Agno**        | ~21.800      | 139            | ~40                              |

> **Conclusão**: Os dados mostram que o **LangChain** é atualmente a ferramenta mais popular e ativa, com uma grande comunidade de desenvolvedores e ritmo elevado de commits. O **AutoGen**, da Microsoft, apresenta também um excelente nível de atividade e conta com a confiança e tradição da empresa no suporte a longo prazo. No momento (24 de março de 2025), a decisão entre LangChain e AutoGen ainda não foi tomada. Entretanto, a tendência é optar pelo **AutoGen**, justamente pela segurança que a Microsoft oferece quanto à continuidade e manutenção das ferramentas, além da documentação robusta. O **LangChain** permanece como uma forte alternativa, destacando-se pela popularidade e adoção comunitária.

---

## 📂 Estrutura planejada do repositório

```bash
agent-flow-craft/
│
├── docs/                  # Documentação completa
├── agents/                # Agentes prontos e templates
├── templates/             # Estruturas genéricas para novos agentes
├── evaluators/            # Avaliadores de conformidades
├── logs/                  # Logs de execução por agente
├── examples/              # Exemplos práticos
├── config/                # Conformidades e parâmetros
├── scripts/               # Scripts utilitários
├── .github/               # Workflows e templates de PR/issue
├── README.md
├── CONTRIBUTING.md
├── LICENSE
└── roadmap.md
```

---

## 🗺 Roadmap Inicial
- [ ] Definir template universal de agente.
- [ ] Criar avaliador genérico de conformidade.
- [ ] Configurar log de tracking unificado.
- [ ] Disponibilizar primeiros agentes de exemplo.
- [ ] Divulgar na comunidade (GitHub, Reddit, Twitter).

---

## 🤝 Como contribuir
1. Faça um fork do repositório.
2. Crie uma branch: `git checkout -b feature/sua-contribuicao`
3. Commit suas mudanças: `git commit -m 'Adiciona nova funcionalidade'`
4. Push para sua branch: `git push origin feature/sua-contribuicao`
5. Abra um Pull Request! 😎

---

## 📜 Licença
Distribuído sob a licença MIT.  
Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## ⭐ Se esse projeto te ajudar, deixe uma estrela no repositório!

---
