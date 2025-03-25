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

# Contribuindo com o AgentFlowCraft

Muito obrigado por querer contribuir! 🎉 Este projeto busca criar um ecossistema sólido para automação de microtarefas utilizando agentes de IA, com rastreamento completo e avaliação automática de conformidades. Aqui estão as diretrizes para ajudar você a contribuir de maneira eficiente.

---

## 📑 Antes de começar
- Leia o [README.md](./README.md) para entender os objetivos do projeto, as ferramentas consideradas e a estrutura planejada.
- Verifique o [roadmap.md](./roadmap.md) para evitar duplicar esforços e alinhar contribuições com as metas do projeto.
- Certifique-se de que há uma *issue* aberta relacionada ao que você deseja contribuir. Caso não exista, crie uma issue primeiro.

---

## 🚀 Como contribuir
1. Faça um **fork** do projeto.
2. Clone o repositório forkado:
   ```bash
   git clone https://github.com/seu-usuario/agent-flow-craft.git
   ```
3. Crie uma nova branch:
   ```bash
   git checkout -b feature/minha-contribuicao
   ```
4. Faça suas alterações e documente bem o que foi feito.
5. Teste localmente, se aplicável.
6. Faça commit das suas alterações:
   ```bash
   git commit -m "Descreva claramente sua contribuição"
   ```
7. Push para o seu fork:
   ```bash
   git push origin feature/minha-contribuicao
   ```
8. Abra um Pull Request detalhado explicando o contexto e o objetivo da sua contribuição.

---

## ✅ Boas práticas
- Escreva commits claros e descritivos.
- Prefira commits pequenos e organizados.
- Mantenha a consistência do código.
- Adicione comentários e documentação, se necessário.
- Atualize o `README.md` ou a documentação, caso sua contribuição afete o uso do projeto.

---

## 📝 Padrões de código
- Utilize Python 3.12+.
- Sempre siga o padrão PEP8.
- Nomeie funções e variáveis de forma autoexplicativa.
- Adicione docstrings quando criar funções ou classes importantes.

---

## 🤝 Código de conduta
Seja respeitoso e colaborativo. Este projeto preza por um ambiente saudável para todos os contribuidores. Confira nosso [Código de Conduta](./CODE_OF_CONDUCT.md) (a ser adicionado em breve).

---

## 📣 Feedback
Sugestões e críticas são sempre bem-vindas! Abra uma *issue* ou entre em contato.

---

## ⭐ Muito obrigado por contribuir!

# Roadmap do AgentFlowCraft

Este documento complementa o [README.md](./README.md) e detalha as etapas previstas e desejáveis para a evolução do projeto.

---

## 🗺 Roadmap Atual

- [ ] Definir template universal de agente.
- [ ] Criar avaliador genérico de conformidade.
- [ ] Configurar sistema de logs centralizados e rastreamento completo.
- [ ] Disponibilizar agentes de exemplo com fluxos completos.
- [ ] Criação de documentação expandida (via `docs/`).
- [ ] Configuração de templates automatizados para novos agentes.
- [ ] Desenvolver painel visual de acompanhamento das execuções.
- [ ] Implementar integração opcional com serviços externos (API OpenAI, Hugging Face, Google Gemini, entre outros).
- [ ] Realizar testes unitários e integração contínua via GitHub Actions.
- [ ] Divulgar para a comunidade (GitHub, Reddit, Twitter, dev.to).

---

## 🏗 Estrutura futura desejada
- Interface web leve para acompanhar logs e loops de correção.
- Criação de uma CLI oficial para facilitar a geração de novos agentes.
- Criação de um marketplace de templates de agentes e conformidades.

---

## 📆 Ciclo de release proposto
- **Lançamentos quinzenais** (ou quando features importantes forem concluídas).
- Versões com changelog bem documentado.
- Releases identificados com versão semântica (exemplo: `v1.0.0`).

---

## 📢 Contribuições para o roadmap
Sugestões são muito bem-vindas!  
Se você tem ideias para o futuro do AgentFlowCraft, abra uma issue ou discuta via Pull Request.

---

## 🌟 Vamos construir juntos!
