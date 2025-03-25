# 🗺 Roadmap do AgentFlowCraft

Este documento acompanha o desenvolvimento do AgentFlowCraft e apresenta o planejamento das próximas etapas, garantindo transparência e organização para colaboradores e usuários.

---

## ✅ Concluído
- Estrutura inicial do repositório
- Documentação principal (README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY)
- Tabelas comparativas de ferramentas e justificativas técnicas
- Criação dos assets visuais ilustrativos
- Estrutura de templates de issues e pull requests

---

## 🚧 Em andamento
- Desenvolvimento do primeiro agente de exemplo com log e avaliação de conformidade
- Integração do avaliador automático e loop de correção
- Estruturação do sistema de fallback para intervenção manual
- Organização da pasta `examples/` com microtarefas demonstrativas
- Criação de um CLI inicial para execução facilitada dos agentes

---

## 🔜 Próximas etapas
- Desenvolvimento de uma interface web leve para acompanhamento dos agentes e logs
- Automatização do deploy via GitHub Actions
- Integração opcional com provedores externos (OpenAI, Hugging Face, Google Gemini)
- Publicação de documentação expandida no GitHub Pages
- Criação de um marketplace de templates de agentes

---

## 📆 Ciclo de releases
- Releases estáveis a cada 2 meses, ou conforme grandes funcionalidades forem concluídas
- Atualizações intermediárias (releases menores) sempre que houver correções críticas ou melhorias incrementais
- Manutenção do changelog para cada release

---

## 🤝 Contribua com o roadmap
Se você tem ideias ou sugestões, fique à vontade para abrir uma issue ou um pull request!  
Este roadmap será atualizado continuamente com a colaboração da comunidade.

---

## 🔎 Primeira feature do projeto: Automação de fluxo de criação de features

**Objetivo:**  
Automatizar o fluxo de criação de novas funcionalidades ou atualizações a partir de um prompt fornecido pelo usuário.

### Etapas desta feature:
- O usuário fornecerá um prompt descrevendo a feature desejada.
- O agente receberá esse prompt, processará a solicitação e:
  - Criará automaticamente uma issue no repositório utilizando a API do GitHub via CLI autenticado.
  - Criará uma branch vinculada à issue aberta.
  - Abrirá um Pull Request relacionado à issue criada.
- Estruturar o projeto para inicialização do primeiro agente responsável por esse fluxo.
- Instalar e configurar a ferramenta **AutoGen da Microsoft** para criação e orquestração do agente.
- Criar arquivos iniciais de configuração e setup do AutoGen no repositório.
- Preparar ambiente local e CI para validação deste fluxo.

### Tarefas manuais iniciais (até automação completa):
- Criar manualmente uma issue, uma PR e uma branch para implementar esta primeira automação.
- Documentar todo o fluxo, padrões e nomenclaturas adotadas no projeto.

**Observação:**  
Essa etapa marca o primeiro uso prático da arquitetura de agentes planejada e estabelece o padrão para todas as próximas automações.

*Última atualização: 24 de março de 2025*
