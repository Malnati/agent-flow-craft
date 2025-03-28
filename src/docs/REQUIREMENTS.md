# Requisitos do Projeto - Agentes Autônomos para Planejamento e Execução

Este documento descreve as **10 etapas principais** para o desenvolvimento do sistema baseado em agentes autônomos. Cada etapa contém seus **entregáveis**, **critérios de aceite**, **troubleshooting**, **passo a passo** e **dependências**.

---

## Etapa 1: Consolidar o agente inicial

### Entregáveis

- Agente inicial funcional com estrutura extensível
- Estrutura de projeto baseada em [django-project-skeleton](https://django-project-skeleton.readthedocs.io/en/latest/structure.html)
- Logging padronizado
- Resultados padronizados
- Suporte ao SDK da OpenAI (Agents, Guardrails, Handoffs, Tools)
- Implementação do Model Context Protocol (MCP)

### Critérios de Aceite

- Agente funcional que cria issue, branch, PR e plano de execução com base no prompt
- Estrutura de arquivos que siga boas práticas Python, pronta para Docker e empacotamento
- Logs completos e informativos
- Uso do MCP com exemplos da [OpenAI](https://github.com/openai/openai-agents-python/tree/main/examples/mcp)

### Troubleshooting

- **Problema:** Plano de execução incompleto  
  **Solução:** Garantir que todos os arquivos e histórico estão sendo submetidos
- **Problema:** Falha de autenticação com GitHub  
  **Solução:** Verificar token e configuração do CLI
- **Problema:** Logs ausentes  
  **Solução:** Validar inicialização de logger e níveis

### Passo a Passo

1. Criar esqueleto do projeto conforme guia de estrutura
2. Implementar funcionalidades iniciais (issue, branch, PR)
3. Adicionar logging e padronização de resultado
4. Integrar ferramentas do Agent SDK da OpenAI
5. Incluir MCP com exemplos reais
6. Validar entregas com testes e critérios definidos

### Dependências

- SDK da OpenAI
- Autogen
- Estrutura django-project-skeleton
- Exemplos de MCP da OpenAI
- Ferramentas: WebSearchTool, FileSearchTool, ComputerTool

---

## Etapa 2: Agente de identificação de entregáveis

### Entregáveis

- Agente que analisa o prompt e o projeto para listar entregáveis
- Cada entregável com: dependências, exemplo, critérios de aceite, troubleshooting e passo a passo
- Validação automática da estrutura de entregáveis

### Critérios de Aceite

- Lista de entregáveis com todos os campos obrigatórios
- Capacidade de reexecutar até obter o formato completo
- Integração com MCP para padronização

### Troubleshooting

- **Problema:** Campos ausentes  
  **Solução:** Solicitar novamente com correções até a completude

### Passo a Passo

1. Criar prompt especializado para identificar entregáveis
2. Enviar prompt e projeto ao modelo via SDK
3. Verificar retorno e, se necessário, repetir
4. Validar e formatar resultado final

### Dependências

- SDK da OpenAI
- Estrutura MCP
- Modelos com suporte a função e contexto
- Histórico do projeto

---

## Etapa 3: Agente de identificação de dependências

### Entregáveis

- Agente que analisa entregáveis para identificar dependências
- Relatório de dependências com detalhes de cada uma

### Critérios de Aceite

- Identificação correta de todas as dependências
- Relatório claro e organizado

### Troubleshooting

- **Problema:** Dependências não identificadas  
  **Solução:** Revisar entregáveis e critérios de análise

### Passo a Passo

1. Analisar entregáveis identificados
2. Listar dependências necessárias
3. Validar relatórios com o modelo

### Dependências

- SDK da OpenAI
- Estrutura de projeto
- Histórico do projeto

---

## Etapa 4: Agente de critério de aceite

### Entregáveis

- Agente que estabelece critérios de aceite para cada entregável
- Documentação dos critérios aplicáveis

### Critérios de Aceite

- Critérios bem definidos e documentados
- Validação com stakeholders

### Troubleshooting

- **Problema:** Critérios não claros  
  **Solução:** Reunir feedback dos stakeholders

### Passo a Passo

1. Definir critérios de aceite
2. Documentar e revisar com a equipe
3. Validar com stakeholders

### Dependências

- Stakeholders
- Documentação do projeto

---

## Etapa 5: Agente de troubleshooting

### Entregáveis

- Agente que gera soluções para problemas identificados
- Base de dados de soluções

### Critérios de Aceite

- Soluções eficazes para problemas comuns
- Documentação acessível

### Troubleshooting

- **Problema:** Soluções ineficazes  
  **Solução:** Revisar e atualizar a base de dados

### Passo a Passo

1. Identificar problemas comuns
2. Documentar soluções
3. Validar com a equipe

### Dependências

- Equipe de suporte
- Base de dados de problemas

---

## Etapa 6: Agente de passo a passo

### Entregáveis

- Agente que fornece passos detalhados para a execução de tarefas
- Documentação clara e acessível

### Critérios de Aceite

- Passos claros e sequenciais
- Validação com usuários finais

### Troubleshooting

- **Problema:** Passos confusos  
  **Solução:** Revisar com usuários finais

### Passo a Passo

1. Listar tarefas a serem executadas
2. Detalhar passos de execução
3. Validar com usuários

### Dependências

- Usuários finais
- Documentação do projeto

---

## Etapa 7: Agente de supervisão de qualidade

### Entregáveis

- Agente que monitora a qualidade das entregas
- Relatórios de qualidade

### Critérios de Aceite

- Relatórios precisos e informativos
- Feedback contínuo para a equipe

### Troubleshooting

- **Problema:** Relatórios imprecisos  
  **Solução:** Revisar critérios de qualidade

### Passo a Passo

1. Definir métricas de qualidade
2. Monitorar entregas
3. Documentar relatórios

### Dependências

- Equipe de qualidade
- Documentação do projeto

---

## Etapa 8: Agente de orquestração autogênica

### Entregáveis

- Agente que coordena a execução de outros agentes
- Relatórios de execução

### Critérios de Aceite

- Coordenação eficaz entre agentes
- Relatórios claros

### Troubleshooting

- **Problema:** Falha na coordenação  
  **Solução:** Revisar lógica de orquestração

### Passo a Passo

1. Definir fluxos de trabalho
2. Implementar orquestração
3. Validar com a equipe

### Dependências

- Outros agentes
- Documentação do projeto

---

## Etapa 9: Agente de definição de modelos e políticas de custo

### Entregáveis

- Agente que define modelos de custo
- Documentação de políticas

### Critérios de Aceite

- Modelos claros e aplicáveis
- Validação com stakeholders

### Troubleshooting

- **Problema:** Modelos confusos  
  **Solução:** Revisar com stakeholders

### Passo a Passo

1. Definir modelos de custo
2. Documentar políticas
3. Validar com stakeholders

### Dependências

- Stakeholders
- Documentação do projeto

---

## Etapa 10: Agente de log e métrica de resultados

### Entregáveis

- Agente que registra logs e métricas de desempenho
- Relatórios de resultados

### Critérios de Aceite

- Logs completos e informativos
- Relatórios claros

### Troubleshooting

- **Problema:** Logs ausentes  
  **Solução:** Validar configuração de logging

### Passo a Passo

1. Implementar sistema de logging
2. Registrar métricas
3. Documentar resultados

### Dependências

- Sistema de logging
- Documentação do projeto

---
