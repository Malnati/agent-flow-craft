#!/usr/bin/env python3
"""
OutGuardrailTDDCriteriaAgent: Agente guardrail responsável por verificar e aprimorar os critérios de aceitação TDD.

Este agente atua após o TDDCriteriaAgent, avaliando se os critérios gerados
atendem a requisitos de qualidade. Se necessário, regenera um prompt otimizado
que inclui:
- O conceito JSON previamente gerado
- Critérios de aceitação TDD gerados pelo TDDCriteriaAgent
- Listagem de arquivos de código-fonte do repositório alvo
- Conteúdo dos arquivos de código-fonte relevantes

O objetivo é garantir critérios TDD de alta qualidade, específicos, e alinhados
com a funcionalidade descrita, focados em APIs/terminal e não em UI.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

try:
    import openai
    has_openai = True
except ImportError:
    has_openai = False

# Tentar importar o logger e funções de logging
try:
    from src.core.logger import get_logger, log_execution
    has_logger = True
except ImportError:
    has_logger = False
    # Logger básico de fallback
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    def get_logger(name):
        return logging.getLogger(name)
    
    def log_execution(func):
        """Decorador simples para logging de execução quando o módulo principal não está disponível"""
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            logger.info(f"INÍCIO - {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"FIM - {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"ERRO - {func.__name__}: {str(e)}", exc_info=True)
                raise
        return wrapper

# Mascaramento básico de dados sensíveis
try:
    from src.core.utils import mask_sensitive_data
    has_utils = True
except ImportError:
    has_utils = False
    def mask_sensitive_data(data, mask_str='***'):
        if isinstance(data, str) and any(s in data.lower() for s in ['token', 'key', 'secret', 'password']):
            if len(data) > 10:
                return f"{data[:4]}{'*' * 12}{data[-4:] if len(data) > 8 else ''}"
            return mask_str
        return data

class OutGuardrailTDDCriteriaAgent:
    """
    Agente guardrail responsável por verificar e aprimorar os critérios de aceitação TDD.
    
    Este agente avalia a qualidade dos critérios gerados pelo TDDCriteriaAgent
    e, se necessário, gera uma versão aprimorada dos critérios focados em funcionalidades
    de API/terminal (não em UI).
    """
    
    def __init__(self, openai_token=None, model="gpt-4-turbo"):
        """
        Inicializa o agente OutGuardrailTDDCriteriaAgent.
        
        Args:
            openai_token (str, optional): Token de acesso à API da OpenAI. Padrão é None,
                                         nesse caso usará a variável de ambiente OPENAI_KEY.
            model (str, optional): Modelo OpenAI a ser utilizado. Padrão é "gpt-4-turbo".
        """
        self.logger = get_logger(__name__)
        self.logger.info(f"INÍCIO - {self.__class__.__name__}.__init__")
        
        self.context_dir = Path("agent_context")
        
        # Configurar token OpenAI
        self.openai_token = openai_token or os.environ.get("OPENAI_KEY", "")
        # Logging seguro do status do token (sem expor o token)
        self.token_status = "presente" if self.openai_token else "ausente"
        self.logger.info(f"Token OpenAI: {self.token_status}")
        
        # Definir modelo a ser utilizado
        self.model = model
        self.logger.info(f"Modelo configurado: {self.model}")
        
        # Criar diretório de contexto se não existir
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Diretório de contexto: {self.context_dir.resolve()}")
        
        self.logger.info(f"FIM - {self.__class__.__name__}.__init__")
    
    def set_model(self, model):
        """
        Define o modelo OpenAI a ser utilizado.
        
        Args:
            model (str): Nome do modelo OpenAI.
        """
        self.logger.info(f"INÍCIO - set_model | Alterando modelo para: {model}")
        self.model = model
        self.logger.info(f"FIM - set_model | Modelo configurado: {self.model}")
    
    @log_execution
    def load_context(self, context_id: str) -> Dict[str, Any]:
        """
        Carrega um arquivo de contexto pelo ID.
        
        Args:
            context_id (str): ID do contexto a ser carregado.
            
        Returns:
            Dict[str, Any]: Dados do contexto carregado, ou dicionário vazio se não encontrado.
        """
        try:
            # Tenta localizar o arquivo de contexto correspondente
            context_file = self.context_dir / f"{context_id}.json"
            
            if not context_file.exists():
                self.logger.warning(f"Arquivo de contexto não encontrado: {context_file}")
                return {}
            
            # Carrega o arquivo JSON
            with open(context_file, 'r', encoding='utf-8') as f:
                context_data = json.load(f)
                
            self.logger.info(f"Contexto carregado com sucesso: {context_id}")
            return context_data
        except Exception as e:
            self.logger.error(f"FALHA - load_context | Erro ao carregar contexto: {str(e)}", exc_info=True)
            return {}
    
    @log_execution
    def list_source_files(self, project_dir: str, extensions: List[str] = None) -> List[str]:
        """
        Lista arquivos de código-fonte no diretório do projeto.
        
        Args:
            project_dir (str): Caminho para o diretório do projeto.
            extensions (List[str], optional): Lista de extensões a considerar.
                                            Padrão é ['.py', '.js', '.ts', '.java', '.go', '.rb'].
                
        Returns:
            List[str]: Lista de caminhos relativos dos arquivos encontrados.
        """
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.java', '.go', '.rb']
            
        project_path = Path(project_dir)
        if not project_path.exists() or not project_path.is_dir():
            self.logger.error(f"Diretório de projeto não existe: {project_dir}")
            return []
            
        # Inicializa lista para guardar os arquivos encontrados
        files = []
        
        # Padrões de pastas a ignorar
        ignore_patterns = ['**/node_modules/**', '**/.git/**', '**/__pycache__/**', '**/.venv/**', '**/venv/**', '**/dist/**', '**/build/**']
        
        # Cria uma lista de todos os arquivos desejados que não estão nas pastas ignoradas
        for ext in extensions:
            for filepath in project_path.glob(f'**/*{ext}'):
                # Verifica se o arquivo deve ser ignorado
                should_ignore = any(filepath.match(pattern) for pattern in ignore_patterns)
                if not should_ignore:
                    # Obtém caminho relativo à raiz do projeto
                    rel_path = filepath.relative_to(project_path)
                    files.append(str(rel_path))
        
        self.logger.info(f"Encontrados {len(files)} arquivos de código-fonte")
        return files
    
    @log_execution
    def read_file_content(self, project_dir: str, file_path: str) -> str:
        """
        Lê o conteúdo de um arquivo específico.
        
        Args:
            project_dir (str): Caminho para o diretório do projeto.
            file_path (str): Caminho relativo do arquivo a ser lido.
            
        Returns:
            str: Conteúdo do arquivo, ou string vazia se não foi possível ler.
        """
        try:
            file_full_path = Path(project_dir) / file_path
            if not file_full_path.exists():
                self.logger.warning(f"Arquivo não encontrado: {file_full_path}")
                return ""
                
            with open(file_full_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
            self.logger.debug(f"Arquivo lido com sucesso: {file_path}")
            return content
        except Exception as e:
            self.logger.error(f"FALHA - read_file_content | Erro ao ler arquivo {file_path}: {str(e)}")
            return ""

    @log_execution
    def evaluate_tdd_criteria(self, tdd_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia a qualidade dos critérios TDD fornecidos.
        
        Args:
            tdd_criteria (Dict[str, Any]): Critérios TDD a serem avaliados.
            
        Returns:
            Dict[str, Any]: Resultado da avaliação.
        """
        result = {
            "is_valid": True,
            "score": 0,
            "issues": [],
            "needs_improvement": False
        }
        
        # Se não tiver critérios, já falha a validação
        if not tdd_criteria or not tdd_criteria.get("criteria"):
            result["is_valid"] = False
            result["score"] = 0
            result["issues"].append("Critérios TDD ausentes ou vazios")
            result["needs_improvement"] = True
            return result
        
        criteria_list = tdd_criteria.get("criteria", [])
        score = 0
        issues = []
        
        # Verificar se existem pelo menos 2 critérios
        if len(criteria_list) < 2:
            issues.append("Número insuficiente de critérios (mínimo recomendado: 2)")
            result["needs_improvement"] = True
        else:
            score += 1
            
        # Verificar a presença de elementos UI em critérios (que devem ser evitados)
        ui_terms = ["tela", "botão", "interface", "ui", "clique", "visualiza", "página", "modal"]
        ui_criteria_count = 0
        
        for criterion in criteria_list:
            # Verificar se todos os campos obrigatórios estão presentes
            required_fields = ["id", "component", "description", "given", "when", "then"]
            missing_fields = [field for field in required_fields if not criterion.get(field)]
            
            if missing_fields:
                issues.append(f"Critério {criterion.get('id', 'sem ID')} está faltando campos: {missing_fields}")
                result["needs_improvement"] = True
            else:
                score += 1
                
            # Verificar critérios de UI
            criterion_text = " ".join([
                str(criterion.get("description", "")),
                str(criterion.get("given", "")),
                str(criterion.get("when", "")),
                str(criterion.get("then", ""))
            ]).lower()
            
            if any(term in criterion_text for term in ui_terms):
                ui_criteria_count += 1
                issues.append(f"Critério {criterion.get('id', 'sem ID')} contém termos de UI, que devem ser evitados")
                result["needs_improvement"] = True
                
        # Verificar plano de testes
        test_plan = tdd_criteria.get("test_plan", {})
        if not test_plan or not any([
            test_plan.get("unit_tests"), 
            test_plan.get("integration_tests"),
            test_plan.get("e2e_tests")
        ]):
            issues.append("Plano de testes ausente ou incompleto")
            result["needs_improvement"] = True
        else:
            score += 1
            
        # Se 50% ou mais dos critérios contêm referências a UI, isso indica problema
        if ui_criteria_count > 0 and ui_criteria_count >= len(criteria_list) * 0.5:
            issues.append("Mais da metade dos critérios contém referências a UI")
            result["needs_improvement"] = True
            score = max(0, score - 1)  # Penalizar a pontuação
            
        # Verificar se é um template padrão
        if tdd_criteria.get("source") == "default_template":
            issues.append("São critérios padrão, não personalizados para a feature")
            result["needs_improvement"] = True
            score = 0
            
        # Calcular pontuação final (0-10)
        max_score = 2 + len(criteria_list)  # Base + 1 ponto por critério
        norm_score = min(10, int((score / max_score) * 10))
        
        result["score"] = norm_score
        result["issues"] = issues
        result["is_valid"] = norm_score >= 7 and not result["needs_improvement"]
        
        return result
    
    @log_execution
    def generate_improved_prompt(self, concept_data: Dict[str, Any], tdd_criteria: Dict[str, Any], 
                                evaluation: Dict[str, Any], project_dir: str, max_files: int = 5) -> str:
        """
        Gera um prompt otimizado para melhorar os critérios TDD existentes.
        
        Args:
            concept_data (Dict[str, Any]): Dados do conceito da feature.
            tdd_criteria (Dict[str, Any]): Critérios TDD existentes.
            evaluation (Dict[str, Any]): Resultado da avaliação dos critérios.
            project_dir (str): Caminho para o diretório do projeto.
            max_files (int, optional): Número máximo de arquivos a incluir. Padrão é 5.
            
        Returns:
            str: Prompt formatado para envio ao modelo.
        """
        # Extrai informações relevantes do conceito
        prompt_text = concept_data.get("prompt", "")
        concept = concept_data.get("concept", {})
        
        # Monta o cabeçalho do prompt
        prompt = f"""# Melhoria de Critérios de Aceitação TDD

## Descrição da Feature
{prompt_text}

## Conceito da Feature
```json
{json.dumps(concept, indent=2, ensure_ascii=False)}
```

## Critérios TDD Existentes
```json
{json.dumps(tdd_criteria, indent=2, ensure_ascii=False)}
```

## Problemas Identificados
{json.dumps(evaluation.get("issues", []), indent=2, ensure_ascii=False)}

"""
        
        # Lista arquivos do projeto
        files = self.list_source_files(project_dir)
        
        # Adiciona listagem de arquivos ao prompt
        prompt += "\n## Arquivos do Projeto\n"
        for file in files[:20]:  # Mais arquivos para dar melhor contexto
            prompt += f"- {file}\n"
            
        # Se houver muitos arquivos, indica que há mais
        if len(files) > 20:
            prompt += f"\n... e mais {len(files) - 20} arquivos\n"
            
        # Tenta encontrar arquivos relevantes com base no conceito da feature
        # e palavras-chave relacionadas a testes/funcionalidades
        issue_title = concept.get("issue_title", "").lower()
        keywords = [word for word in issue_title.split() if len(word) > 3]
        
        # Adiciona palavras-chave relacionadas a testes/funcionalidades comuns
        extra_keywords = ["test", "api", "function", "endpoint", "cli", "command", "terminal", 
                          "interface", "service", "controller", "model", "agent"]
        keywords.extend(extra_keywords)
        
        # Seleciona arquivos que contêm palavras-chave no caminho
        relevant_files = [
            file for file in files
            if any(keyword in file.lower() for keyword in keywords)
        ]
        
        # Se não encontrou arquivos relevantes, usa os primeiros da lista
        if not relevant_files and files:
            relevant_files = files[:min(max_files, len(files))]
            
        # Adiciona conteúdo dos arquivos relevantes
        prompt += "\n## Conteúdo de Arquivos Relevantes\n"
        
        for file in relevant_files[:max_files]:
            content = self.read_file_content(project_dir, file)
            if content:
                # Limita o tamanho para não exceder limites de tokens
                max_chars = 1500
                truncated = content[:max_chars] + ("..." if len(content) > max_chars else "")
                prompt += f"\n### Arquivo: {file}\n```\n{truncated}\n```\n"
                    
        # Adiciona instruções específicas para o modelo
        prompt += """
## Instruções
Com base no conceito da feature, nos critérios TDD existentes e nos problemas identificados, gere uma versão aprimorada 
de critérios de aceitação TDD. Os novos critérios devem:

1. Ser específicos, testáveis e claros
2. Cobrir casos de uso principais e casos de borda
3. Seguir o formato "DADO... QUANDO... ENTÃO..."
4. Ser organizados por componente ou funcionalidade 
5. NÃO incluir elementos de UI (telas, botões, cliques) - concentre-se em API, CLI e funcionalidade
6. Incluir exemplos de entradas e saídas esperadas quando aplicável
7. Especificar valores limites em casos numéricos
8. Incluir testes para tratamento de erros e exceções
9. Abordar aspectos de segurança, performance ou escalabilidade quando relevante

## Formato da Resposta
```json
{
  "criteria": [
    {
      "id": "TDD-001",
      "component": "nome do componente",
      "description": "descrição do critério",
      "given": "condição inicial",
      "when": "ação realizada",
      "then": "resultado esperado",
      "edge_cases": ["caso de borda 1", "caso de borda 2"],
      "examples": [
        {"input": "exemplo de entrada", "output": "exemplo de saída esperada"}
      ]
    }
  ],
  "test_plan": {
    "unit_tests": ["descrição do teste unitário 1", "descrição do teste unitário 2"],
    "integration_tests": ["descrição do teste de integração 1"],
    "e2e_tests": ["descrição do teste e2e 1"]
  }
}
```
"""
        return prompt
    
    @log_execution
    def improve_tdd_criteria(self, criteria_id: str, concept_id: str, project_dir: str) -> Dict[str, Any]:
        """
        Avalia e melhora os critérios TDD existentes.
        
        Args:
            criteria_id (str): ID dos critérios TDD a melhorar.
            concept_id (str): ID do conceito da feature.
            project_dir (str): Caminho para o diretório do projeto.
            
        Returns:
            Dict[str, Any]: Critérios TDD melhorados, ou dicionário original se não houver melhorias.
        """
        try:
            # Verifica se tem token OpenAI
            if not self.openai_token:
                self.logger.warning("Token OpenAI ausente. Não é possível melhorar os critérios.")
                return {
                    "error": "Token OpenAI ausente",
                    "message": "É necessário um token OpenAI válido para melhorar os critérios TDD."
                }
            
            # Carrega os critérios TDD existentes
            criteria_data = self.load_context(criteria_id)
            if not criteria_data:
                self.logger.error(f"Critérios TDD não encontrados para o ID: {criteria_id}")
                return {"error": f"Critérios TDD não encontrados para o ID: {criteria_id}"}
            
            # Extrai os critérios do objeto de contexto
            tdd_criteria = criteria_data.get("criteria", {})
            
            # Carrega o conceito da feature
            concept_data = self.load_context(concept_id)
            if not concept_data:
                self.logger.error(f"Conceito não encontrado para o ID: {concept_id}")
                return {"error": f"Conceito não encontrado para o ID: {concept_id}"}
            
            # Avalia os critérios existentes
            evaluation = self.evaluate_tdd_criteria(tdd_criteria)
            self.logger.info(f"Avaliação de critérios: Pontuação={evaluation['score']}/10, " +
                            f"Válido={evaluation['is_valid']}, Precisa melhorias={evaluation['needs_improvement']}")
            
            # Se os critérios já são bons o suficiente, retorna os originais
            if evaluation["is_valid"] and not evaluation["needs_improvement"]:
                self.logger.info("Os critérios TDD existentes são adequados. Nenhuma melhoria necessária.")
                return tdd_criteria
                
            # Caso contrário, gera um prompt para melhorar os critérios
            prompt = self.generate_improved_prompt(concept_data, tdd_criteria, evaluation, project_dir)
            
            # Configura o cliente OpenAI
            openai.api_key = self.openai_token
            
            # Solicita os critérios TDD melhorados ao modelo
            self.logger.info(f"Enviando solicitação à API OpenAI (modelo: {self.model}) para melhorar os critérios...")
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um especialista em Test-Driven Development focado em critérios de aceitação para APIs, CLIs e funcionalidades (não para UI)."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Baixa temperatura para respostas mais consistentes
                max_tokens=4000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extrai a resposta da API
            answer = response.choices[0].message.content.strip()
            
            # Tenta extrair o JSON da resposta
            json_start = answer.find('```json')
            json_end = answer.rfind('```')
            
            if json_start >= 0 and json_end > json_start:
                json_str = answer[json_start + 7:json_end].strip()
                try:
                    improved_criteria = json.loads(json_str)
                    # Adiciona metadados
                    improved_criteria["context_id"] = concept_id
                    improved_criteria["original_criteria_id"] = criteria_id
                    improved_criteria["generated_at"] = datetime.now().isoformat()
                    improved_criteria["model_used"] = self.model
                    improved_criteria["improved"] = True
                    
                    # Salva os critérios melhorados no diretório de contexto
                    improved_id = f"tdd_improved_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    self._save_improved_to_context(improved_id, improved_criteria, concept_id, criteria_id)
                    
                    improved_criteria["context_id"] = improved_id
                    return improved_criteria
                except json.JSONDecodeError as e:
                    self.logger.error(f"FALHA - Erro ao decodificar JSON: {str(e)}")
                    # Retorna texto bruto se falhar ao decodificar JSON
                    return {
                        "error": "Formato JSON inválido",
                        "raw_content": answer,
                        "original_criteria_id": criteria_id
                    }
            else:
                # Se não conseguir extrair JSON, retorna o texto completo
                return {
                    "error": "Não foi possível extrair JSON da resposta",
                    "raw_content": answer,
                    "original_criteria_id": criteria_id
                }
                
        except Exception as e:
            self.logger.error(f"FALHA - improve_tdd_criteria | Erro: {str(e)}", exc_info=True)
            return {
                "error": f"Erro ao melhorar critérios TDD: {str(e)}",
                "original_criteria_id": criteria_id
            }
    
    @log_execution
    def _save_improved_to_context(self, criteria_id: str, criteria: Dict[str, Any], 
                               concept_id: str, original_criteria_id: str) -> str:
        """
        Salva os critérios TDD melhorados no diretório de contexto.
        
        Args:
            criteria_id (str): ID único para os critérios melhorados.
            criteria (Dict[str, Any]): Critérios TDD melhorados a serem salvos.
            concept_id (str): ID do contexto do conceito relacionado.
            original_criteria_id (str): ID dos critérios originais.
            
        Returns:
            str: ID do arquivo de critérios salvo.
        """
        try:
            # Cria o diretório de contexto se não existir
            self.context_dir.mkdir(parents=True, exist_ok=True)
            
            # Cria o arquivo de contexto
            context_file = self.context_dir / f"{criteria_id}.json"
            
            # Adiciona metadados
            metadata = {
                "id": criteria_id,
                "type": "tdd_improved_criteria",
                "concept_id": concept_id,
                "original_criteria_id": original_criteria_id,
                "created_at": datetime.now().isoformat(),
                "criteria": criteria
            }
            
            # Salva o arquivo
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Critérios TDD melhorados salvos em: {context_file}")
            return criteria_id
            
        except Exception as e:
            self.logger.error(f"FALHA - _save_improved_to_context | Erro: {str(e)}", exc_info=True)
            return ""
    
    @log_execution
    def execute_tdd_guardrail(self, criteria_id: str, concept_id: str, project_dir: str) -> Dict[str, Any]:
        """
        Função principal que executa o guardrail para os critérios TDD.
        Avalia, e se necessário, melhora os critérios.
        
        Args:
            criteria_id (str): ID dos critérios TDD a avaliar.
            concept_id (str): ID do conceito da feature.
            project_dir (str): Caminho para o diretório do projeto.
            
        Returns:
            Dict[str, Any]: Resultado da execução do guardrail.
        """
        try:
            # Carrega os critérios TDD existentes
            criteria_data = self.load_context(criteria_id)
            if not criteria_data:
                self.logger.error(f"Critérios TDD não encontrados para o ID: {criteria_id}")
                return {"error": f"Critérios TDD não encontrados para o ID: {criteria_id}"}
            
            # Extrai os critérios do objeto de contexto
            tdd_criteria = criteria_data.get("criteria", {})
            
            # Avalia os critérios existentes
            evaluation = self.evaluate_tdd_criteria(tdd_criteria)
            self.logger.info(f"Avaliação de critérios: Pontuação={evaluation['score']}/10, " +
                            f"Válido={evaluation['is_valid']}, Precisa melhorias={evaluation['needs_improvement']}")
            
            result = {
                "original_criteria_id": criteria_id,
                "concept_id": concept_id,
                "evaluation": evaluation,
                "criteria": tdd_criteria
            }
            
            # Se os critérios precisam ser melhorados, tenta melhorá-los
            if evaluation["needs_improvement"] or not evaluation["is_valid"]:
                self.logger.info("Os critérios TDD precisam de melhorias. Tentando melhorar...")
                
                if not self.openai_token:
                    self.logger.warning("Token OpenAI ausente. Não é possível melhorar os critérios.")
                    result["warning"] = "Token OpenAI ausente. Não foi possível melhorar os critérios."
                    return result
                
                # Melhora os critérios
                improved_criteria = self.improve_tdd_criteria(criteria_id, concept_id, project_dir)
                
                # Verifica se houve erro na melhoria
                if "error" in improved_criteria:
                    result["error"] = improved_criteria["error"]
                    if "raw_content" in improved_criteria:
                        result["raw_content"] = improved_criteria["raw_content"]
                    return result
                
                # Atualiza o resultado com os critérios melhorados
                result["improved_criteria_id"] = improved_criteria.get("context_id")
                result["criteria"] = improved_criteria
                result["was_improved"] = True
                
                return result
            else:
                # Se os critérios já são bons, apenas retorna o resultado
                result["message"] = "Os critérios TDD existentes são adequados. Nenhuma melhoria necessária."
                result["was_improved"] = False
                
                return result
                
        except Exception as e:
            self.logger.error(f"FALHA - execute_tdd_guardrail | Erro: {str(e)}", exc_info=True)
            return {
                "error": f"Erro ao executar o guardrail TDD: {str(e)}",
                "criteria_id": criteria_id,
                "concept_id": concept_id
            } 