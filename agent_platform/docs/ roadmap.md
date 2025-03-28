# 🗺 Roadmap do AgentFlowCraft

Este documento acompanha o desenvolvimento do AgentFlowCraft e apresenta um planejamento estruturado e transparente para colaboradores, contribuidores e usuários. Ele serve como guia estratégico para o crescimento do projeto e a organização das entregas.

---

## ✅ Concluído
- Estrutura inicial do repositório.
- Documentação principal (README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SUPPORT, CHANGELOG).
- Tabelas comparativas de ferramentas e justificativas técnicas de escolha.
- Criação de assets visuais e diagramas ilustrativos.
- Estruturação de templates de issues e pull requests.
- Configuração de workflows GitHub Actions para validações (código, markdown, YAML, assets).
- Configuração inicial do semantic-release e versionamento automático.

---

## 🚧 Em andamento
- Desenvolvimento do primeiro agente de exemplo com registro de raciocínio e logs.
- Implementação do avaliador automático de conformidade com loop de correção.
- Criação do fallback para intervenção manual em caso de bloqueio.
- Organização da pasta `examples/` com microtarefas demonstrativas.
- Estruturação de um CLI inicial para facilitar a execução dos agentes.
- Preparação do ambiente local e CI para suporte completo ao AutoGen da Microsoft.

---

## 🔜 Próximas etapas
- Desenvolvimento de uma interface web leve para acompanhamento dos agentes, execução e visualização de logs.
- Automação do deploy contínuo via GitHub Actions.
- Integração opcional com provedores externos (OpenAI, Hugging Face, Google Gemini).
- Publicação de documentação completa e interativa no GitHub Pages.
- Criação de um marketplace público de templates de agentes, disponível na pasta `templates/`.
- Criação de um agente monitor de workflows (para automação da manutenção do repositório).

---

## 📆 Ciclo de releases
- **Releases estáveis:** a cada 2 meses ou conforme entrega de funcionalidades-chave.
- **Releases intermediárias:** sempre que houver correções críticas ou melhorias incrementais importantes.
- **Changelog:** atualizado automaticamente via semantic-release a cada versão.
- **Tags:** geradas automaticamente utilizando Conventional Commits + semantic-release.

---

## 🤝 Como contribuir para o roadmap
Se você deseja sugerir novas funcionalidades, melhorias ou ajustes, siga os passos:
1. Abra uma issue do tipo *Feature Request* utilizando o template.
2. Descreva claramente o problema, contexto, proposta e impacto esperado.
3. Participe das discussões e acompanhe o status da proposta.

Este roadmap será atualizado continuamente com a colaboração da comunidade.

---

## 🔎 Primeira grande feature: Automação do fluxo de criação de features

**Objetivo:**  
Permitir que o usuário envie um prompt descrevendo uma funcionalidade desejada e que um agente automatize:  
- Criação de issue via API do GitHub utilizando CLI autenticado.
- Criação de uma branch vinculada à issue.
- Abertura de um Pull Request automatizado relacionado à issue.

### Passos desta implementação:
- Definir e documentar o fluxo completo.
- Instalar e configurar o AutoGen da Microsoft.
- Criar os primeiros arquivos de configuração do agente.
- Desenvolver o agente inicial e scripts auxiliares.
- Validar o processo manualmente e posteriormente via CI.

### Tarefas manuais iniciais:
- Criar a primeira issue, branch e PR manualmente seguindo o padrão.
- Estabelecer as nomenclaturas oficiais de branches e mensagens de commit.
- Registrar todos os aprendizados no `docs/` para uso futuro.

**Nota importante:**  
Este será o marco inicial do projeto, estabelecendo o padrão de automação para todas as features futuras.

---

*Última atualização: 25 de março de 2025*
