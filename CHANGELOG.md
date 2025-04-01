## Unreleased

### BREAKING CHANGE

-  foi adicionado à biblioteca commitizen

### Feat

- **Adiciona-o-commitizen-E-automatiza-o-controle-de-versões**: é um controle diversões semi-automatizado com o commitizen
- atualiza Makefile e setup.py para nova versão e registro de commits
- Adicionar agente de refatoração (RefactorAgent) ao Makefile e documentação
- Remover arquivos de requisitos de planos de execução obsoletos
- Adicionar arquivo de requisitos para planos de execução com validações e exemplos
- Atualizar dependências do ambiente virtual e remover configuração obsoleta
- Adicionar exclusão de arquivos JSON do contexto do agente ao .gitignore
- Remover arquivos de conceito, critérios de TDD e melhorias obsoletos relacionados à correção de nomes de branches
- Atualizar lógica de extração de dados de conceito no agente de integração do GitHub
- Adicionar suporte a modelos de elevação e opção de força em agentes de geração e coordenação
- Atualizar mensagens de uso e remover arquivo de resultado de orquestração obsoleto
- Remover arquivos de conceito e critérios de TDD obsoletos relacionados ao cadastro de perfil de usuários
- Adicionar agente de feature concept e atualizar fluxos de geração de conceitos no sistema de criação de features
- Remover arquivos desnecessários e corrigir importações no script start_feature_agent.py
- Atualizar resultado da orquestração com novos critérios de TDD, melhorias na descrição e tratamento de erros do hook useSearchParams
- Atualizar resultado da orquestração com novos critérios de TDD e melhorias na validação
- Implementar validação obrigatória de tokens para todos os agentes
- Atualizar resultado da orquestração com novos parâmetros e melhorias no contexto
- Integrar ConceptGuardrailAgent no fluxo de coordenação
- Implementar ConceptGuardrailAgent para validação e melhoria de conceitos
- Adicionar suporte ao TDDGuardrailAgent no Makefile e atualizar documentação de uso
- atualiza Makefile para unificar comandos e melhorar a configura… (#86)
- atualiza Makefile para unificar comandos e melhorar a configuração do ambiente
- atualiza Makefile para empacotamento e implantação do MCP
- adiciona comando de desinstalação do MCP e atualiza documentação
- adiciona instalação simplificada do MCP e atualiza documentação
- adiciona agente de criação de features e melhorias na configuração do MCP Server
- adiciona função assíncrona para inicialização de agentes locais
- adiciona inicialização de agentes locais a partir de configuração YAML
- atualiza workflow de lint para verificar correspondência de branch (#66)
- release
- atualiza workflow de lint para verificar correspondência de branch (#66)
- release

### Fix

- Corrigir importações e compatibilidade do PYTHONPATH
- Remover importações de módulos inexistentes
- Corrigir parâmetros do TDDGuardrailAgent no script run_tdd_guardrail_agent.py

### Refactor

- atualiza Makefile e setup.py para instalação de dependências
- Atualizar importações para remover o prefixo 'src' e padronizar caminhos
- Consolidar estrutura movendo agent_platform para core
- Padronizar caminho do arquivo plan_requirements.yaml para src/configs/agents/
- Move test_feature_concept_agent.py from tests/ to src/tests/
- Renomear agentes guardrail para OutGuardrail e atualizar scripts de execução
- Padronizar nomenclatura de guardrails para facilitar rastreamento
