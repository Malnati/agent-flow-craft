## 📝 Prompt completo sugerido para o agente

> Abaixo segue o prompt ideal a ser utilizado pelo agente de IA (Copilot ou equivalente) para criar o primeiro agente responsável por automatizar o fluxo de criação de features, incluindo todas as etapas necessárias, desde a preparação do ambiente até a execução completa do fluxo.

---

**Prompt:**

Você é um agente encarregado de criar o primeiro agente funcional do projeto **AgentFlowCraft**. Este agente deverá automatizar o processo de criação de features a partir de prompts fornecidos pelos usuários. Siga detalhadamente as etapas abaixo e gere todos os arquivos, configurações e orientações necessárias:

1. **Instalação e configuração:**
   - Verifique se o ambiente Python está configurado.
   - Instale o pacote `pyautogen` utilizando `uv pip install pyautogen`.
   - Adicione essa dependência no arquivo de controle (`requirements.txt` ou `pyproject.toml`).
   - Certifique-se de que o GitHub CLI (`gh`) esteja disponível e autenticado.

2. **Criação do agente principal:**
   - Crie um arquivo `agents/feature_creation_agent.py`.
   - O agente deve:
     - Receber um prompt do usuário.
     - Criar automaticamente uma issue no repositório via GitHub CLI.
     - Obter e armazenar o número da issue criada.
     - Criar uma branch vinculada à issue (`feature/issue-<issue_number>`).
     - Gerar um plano de execução detalhado baseado no prompt e salvar no diretório `docs/pr/` como `<issue_number>_feature_plan.md`.
     - Fazer commit e push deste arquivo.
     - Abrir um Pull Request automaticamente vinculado à issue criada, contendo o link para o plano de execução.

3. **Configuração de ambiente e scripts:**
   - Adicione logs detalhados de cada etapa na pasta `logs/`.
   - Crie um script CLI simples (`src/scripts/start_feature_agent.py`) para facilitar a execução do agente via terminal.

4. **Testes:**
   - Crie um arquivo inicial de testes automatizados para o agente, dentro de `tests/test_feature_creation_agent.py`.
   - Assegure que os testes cubram:
     - Criação simulada de issue.
     - Geração de branch e plano de execução.
     - Simulação de abertura de PR.

5. **Documentação:**
   - Atualize o `docs/README.md` referenciando o novo agente.
   - Inclua instruções para execução local.

6. **Checklist final:**
   - Valide se todos os arquivos foram criados.
   - Faça commit e push de todas as alterações.
   - Confirme o funcionamento do fluxo completo localmente.

Ao concluir, informe o usuário com um resumo e indique o caminho para o plano de execução e o PR criado.

---
