# 📂 Diretório `docs/pr/`

Este diretório contém planos de execução detalhados para as issues criadas e pull requests abertos pelo agente de criação de features. Cada arquivo neste diretório segue o formato `<issue_number>_feature_plan.md` e inclui:

- **Prompt recebido:** O prompt original fornecido pelo usuário.
- **Plano de execução gerado pela IA:** Um plano detalhado de como a funcionalidade será implementada, incluindo contexto, descrição da solução, alternativas consideradas, checklist técnico de implementação e observações adicionais.

## Estrutura dos arquivos

Cada arquivo de plano de execução contém as seguintes seções:

1. **Título:** `Plano de execução para a issue #<issue_number>`
2. **Prompt recebido:** O prompt original fornecido pelo usuário.
3. **Plano de execução gerado pela IA:** Um plano detalhado de como a funcionalidade será implementada, incluindo:
   - Contexto
   - Descrição da solução
   - Alternativas consideradas
   - Checklist técnico de implementação
   - Observações adicionais

## Exemplo de arquivo de plano de execução

```markdown
# Plano de execução para a issue #123

**Prompt recebido:** Adicionar funcionalidade de login social com Google e Facebook.

**Plano de execução gerado pela IA:**

### Contexto
A funcionalidade de login social permitirá que os usuários façam login utilizando suas contas do Google ou Facebook, facilitando o processo de autenticação e melhorando a experiência do usuário.

### Descrição da solução
1. Integrar a API de autenticação do Google.
2. Integrar a API de autenticação do Facebook.
3. Adicionar botões de login social na página de login.
4. Implementar o fluxo de autenticação no backend.
5. Testar a funcionalidade em diferentes navegadores e dispositivos.

### Alternativas consideradas
- Utilizar outras redes sociais como Twitter ou LinkedIn.
- Implementar autenticação via email e senha como alternativa.

### Checklist técnico de implementação
- [ ] Configurar credenciais de API para Google e Facebook.
- [ ] Implementar integração com a API do Google.
- [ ] Implementar integração com a API do Facebook.
- [ ] Adicionar botões de login social na interface do usuário.
- [ ] Implementar fluxo de autenticação no backend.
- [ ] Testar a funcionalidade em diferentes navegadores e dispositivos.

### Observações adicionais
Certifique-se de que todas as credenciais de API estejam armazenadas de forma segura e que a integração esteja em conformidade com as políticas de privacidade das redes sociais.

```

## Atualização automática

O índice dos planos de execução neste diretório é atualizado automaticamente via workflow do GitHub Actions. Sempre que um novo plano de execução é criado, ele será adicionado ao índice na documentação principal (`docs/README.md`).

# Planos de Execução de PR

Este diretório contém arquivos de plano de execução para pull requests. Cada arquivo segue o formato `<issue_number>_feature_plan.md`.

## Formato do Plano de Execução

Cada plano de execução contém as seguintes seções:

1. **Cabeçalho**: Título da issue e número
2. **Prompt Recebido**: O prompt original enviado pelo usuário
3. **Plano de Execução**: Detalhes do plano gerado automaticamente, que inclui:

### Entregáveis

Para cada entregável, o plano inclui:

- **Nome**: Nome claro e específico do entregável
- **Descrição**: Descrição detalhada incluindo propósito e funcionalidade
- **Dependências**: Lista de dependências necessárias (bibliotecas, serviços, etc.)
- **Exemplo de Uso**: Exemplo prático de como usar o entregável
- **Critérios de Aceitação**: Lista de critérios mensuráveis para validar o entregável
- **Resolução de Problemas**: Possíveis problemas, causas e soluções
- **Passos de Implementação**: Lista detalhada de passos para implementar o entregável

## Exemplo

```markdown
# Plano de execução para a issue #42

**Prompt recebido:** Criar um sistema de autenticação

**Plano de execução gerado automaticamente:**

## Detalhes do Plano

### Entregável 1: Sistema de Autenticação OAuth2

**Descrição:** Sistema de autenticação usando OAuth2 para integração com serviços externos.

**Dependências:**
- oauth2-client v2.1.0
- jsonwebtoken v8.5.1
- secure-storage v1.2.0

**Exemplo de uso:**
```
const auth = new OAuth2Auth(config);
const token = await auth.authenticate(user, password);
```

**Critérios de aceitação:**
- Autenticação com Google e GitHub funciona corretamente
- Tokens são armazenados de forma segura
- Sistema de refresh token implementado

**Resolução de problemas:**
- Problema: Token expirado
  - Causa possível: Tempo de expiração muito curto
  - Resolução: Implementar refresh automático de token

**Passos de implementação:**
1. Configurar cliente OAuth2
2. Implementar endpoints de autenticação
3. Criar sistema de armazenamento seguro de tokens
4. Implementar mecanismo de refresh token
5. Testar integrações com provedores
```

## Uso

Os planos de execução são gerados automaticamente quando uma nova issue é criada. O plano é então usado como base para o desenvolvimento da feature e é referenciado na pull request.

