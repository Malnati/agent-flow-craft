# 📜 Changelog

Todas as mudanças notáveis neste projeto serão documentadas aqui.

Este projeto segue o [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [Não publicado]

### Adicionado
- Implementação inicial do `FeatureCreationAgent` para automatizar o fluxo de criação de features
- Script CLI `start_feature_agent.py` para facilitar a execução do agente
- Criação de testes automatizados para o agente de criação de features
- Novo método `check_github_auth` para verificar a autenticação do GitHub CLI antes de executar ações
- Adicionado timeout para comandos de subprocesso para evitar bloqueios
- Inclusão de logs detalhados para rastreamento de ações do agente
- Script `run_coverage.py` para gerar relatórios de cobertura de testes

### Alterado
- Substituição de timeouts fixos por timeouts dinâmicos nas chamadas de subprocesso
- Parâmetros `--owner` e `--repo` agora são obrigatórios no CLI, com mensagens de erro melhoradas

### Inicial
- Configuração inicial do projeto.
- Adição do README, CONTRIBUTING, CODE_OF_CONDUCT e ROADMAP.
- Criação dos assets visuais e diagramas.
- Estruturação de automações via GitHub Actions (validação de código, markdown, YAML e assets).
- Configuração do semantic-release para versionamento automático.
