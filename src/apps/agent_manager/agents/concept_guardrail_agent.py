#!/usr/bin/env python3
"""
ConceptGuardrailAgent: Agente guardrail responsável por validar e aprimorar os conceitos de feature.

Este agente atua após o ConceptGenerationAgent, avaliando se o conceito gerado (concept.json) 
segue um fluxo determinístico claro. Se necessário, regenera um prompt otimizado
que inclui:
- O conceito JSON previamente gerado
- Avaliação dos problemas com o conceito atual
- Listagem de arquivos de código-fonte do repositório alvo
- Conteúdo dos arquivos de código-fonte relevantes

O objetivo é garantir conceitos de alta qualidade, específicos, determinísticos 
e alinhados com a funcionalidade solicitada pelo usuário.
"""

import os
import sys
import json
import logging
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import tracemalloc

try:
    import openai
    has_openai = True
except ImportError:
    has_openai = False

# Tentar importar o logger e funções de logging
try:
    from agent_platform.core.logger import get_logger, log_execution
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
    from agent_platform.core.utils import mask_sensitive_data, get_env_status
    has_utils = True
except ImportError:
    has_utils = False
    def mask_sensitive_data(data, mask_str='***'):
        if isinstance(data, str) and any(s in data.lower() for s in ['token', 'key', 'secret', 'password']):
            if len(data) > 10:
                return f"{data[:4]}{'*' * 12}{data[-4:] if len(data) > 8 else ''}"
            return mask_str
        return data

class ConceptGuardrailAgent:
    """
    Agente guardrail responsável por validar e aprimorar os conceitos de feature.
    
    Este agente avalia a qualidade dos conceitos gerados pelo ConceptGenerationAgent
    e, se necessário, gera versões aprimoradas dos conceitos quando estes não contêm
    um fluxo determinístico claro ou estão muito genéricos.
    """
    
    def __init__(self, openai_token=None, model="gpt-4-turbo"):
        """
        Inicializa o agente ConceptGuardrailAgent.
        
        Args:
            openai_token (str, optional): Token de acesso à API da OpenAI. Padrão é None,
                                         nesse caso usará a variável de ambiente OPENAI_API_KEY.
            model (str, optional): Modelo OpenAI a ser utilizado. Padrão é "gpt-4-turbo".
        """
        self.logger = get_logger(__name__)
        self.logger.info(f"INÍCIO - {self.__class__.__name__}.__init__")
        
        self.context_dir = Path("agent_context")
        
        # Configurar token OpenAI
        self.openai_token = openai_token or os.environ.get("OPENAI_API_KEY", "")
        # Logging seguro do status do token (sem expor o token)
        self.token_status = "presente" if self.openai_token else "ausente"
        self.logger.info(f"Token OpenAI: {self.token_status}")
        
        # Definir modelo a ser utilizado
        self.model = model
        self.logger.info(f"Modelo configurado: {self.model}")
        
        # Criar diretório de contexto se não existir
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Diretório de contexto: {self.context_dir.resolve()}")
        
        # Iniciando rastreamento de memória e execução para trace
        tracemalloc.start()
        
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
                # Tentar buscar com wildcard
                pattern = f"{context_id}*.json"
                matches = list(self.context_dir.glob(pattern))
                if matches:
                    context_file = matches[0]
                    self.logger.info(f"Contexto encontrado com wildcard: {context_file.name}")
                else:
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
        ignore_patterns = ['**/node_modules/**', '**/.git/**', '**/__pycache__/**', 
                           '**/.venv/**', '**/venv/**', '**/dist/**', '**/build/**']
        
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
    def evaluate_concept(self, concept: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia a qualidade do conceito fornecido.
        
        Args:
            concept (Dict[str, Any]): Conceito a ser avaliado.
            
        Returns:
            Dict[str, Any]: Resultado da avaliação.
        """
        result = {
            "is_valid": True,
            "score": 0,
            "issues": [],
            "needs_improvement": False
        }
        
        # Se não tiver conceito, já falha a validação
        if not concept:
            result["is_valid"] = False
            result["score"] = 0
            result["issues"].append("Conceito ausente ou vazio")
            result["needs_improvement"] = True
            return result
        
        score = 0
        issues = []
        
        # Verificar elementos obrigatórios
        required_fields = ["branch_type", "issue_title", "issue_description", "execution_plan"]
        for field in required_fields:
            if field not in concept:
                issues.append(f"Campo obrigatório ausente: {field}")
                result["is_valid"] = False
            else:
                score += 1
                
        # Verificar se tem plano de execução
        if "execution_plan" in concept:
            execution_plan = concept["execution_plan"]
            
            # Verificar se execution_plan é um dicionário ou lista
            if isinstance(execution_plan, dict):
                # Verificar se tem steps no plano
                if "steps" in execution_plan and isinstance(execution_plan["steps"], list):
                    steps = execution_plan["steps"]
                    
                    # Verificar número mínimo de passos
                    if len(steps) < 2:
                        issues.append("Plano de execução tem menos de 2 passos")
                        score -= 1
                    else:
                        score += 2
                        
                    # Verificar se os passos são descritivos (não apenas palavras soltas)
                    generic_steps = []
                    for step in steps:
                        # Verificar o comprimento e conteúdo do passo
                        if len(step) < 10 or not any(char.isalpha() for char in step):
                            generic_steps.append(step)
                            
                    if generic_steps:
                        issues.append(f"{len(generic_steps)} passos são genéricos ou curtos demais")
                        score -= 1
                else:
                    issues.append("Plano de execução não contém lista de passos ('steps')")
                    score -= 2
            else:
                issues.append("Plano de execução não é um objeto estruturado")
                score -= 2
        
        # Verificar título e descrição genéricos
        generic_title_patterns = ["implementation", "feature", "system", "functionality", "add ", "implement "]
        if "issue_title" in concept:
            title = concept["issue_title"].lower()
            if any(pattern in title for pattern in generic_title_patterns) and len(title.split()) < 4:
                issues.append("Título da issue é genérico")
                score -= 1
        
        # Verificar descrição genérica ou curta
        if "issue_description" in concept:
            description = concept["issue_description"]
            if len(description) < 20:
                issues.append("Descrição da issue é muito curta")
                score -= 1
            
            # Verificar se é igual ao título (sem detalhamento)
            if "issue_title" in concept and description.lower() == concept["issue_title"].lower():
                issues.append("Descrição da issue é idêntica ao título (sem detalhamento)")
                score -= 1
        
        # Análise de determinismo
        determinism_score = 0
        max_determinism_score = 5
        
        # Verificar se os passos têm ordem clara (números, sequência lógica)
        if "execution_plan" in concept and isinstance(concept["execution_plan"], dict) and "steps" in concept["execution_plan"]:
            steps = concept["execution_plan"]["steps"]
            
            # Verificar se os passos têm numeração
            numbered_steps = [step for step in steps if re.match(r'^\d+[\.\)\-]?\s+.*', step)]
            if len(numbered_steps) == len(steps) and len(steps) > 0:
                determinism_score += 2
            
            # Verificar se há palavras indicativas de sequência
            sequence_words = ["first", "initially", "then", "next", "after", "finally", "lastly"]
            has_sequence_words = any(word in " ".join(steps).lower() for word in sequence_words)
            if has_sequence_words:
                determinism_score += 1
                
            # Verificar relações entre etapas
            if "entregáveis" in str(concept).lower() or "deliverables" in str(concept).lower():
                determinism_score += 1
                
            # Verificar requisitos detalhados
            if "requisitos" in str(concept).lower() or "requirements" in str(concept).lower():
                determinism_score += 1
        
        # Adicionar pontuação de determinismo à pontuação geral
        score += determinism_score
        
        # Normalizar a pontuação para uma escala de 0 a 10
        max_score = 6 + max_determinism_score  # campos básicos (4) + passos bem formados (2) + determinismo (5)
        normalized_score = min(10, int((score / max_score) * 10))
        
        # Preencher o resultado
        result["score"] = normalized_score
        result["issues"] = issues
        result["determinism_score"] = determinism_score
        result["max_determinism_score"] = max_determinism_score
        
        # Determinar se precisa de melhoria
        result["needs_improvement"] = normalized_score < 6 or len(issues) > 2 or determinism_score < 3
        
        return result

    @log_execution
    def create_improvement_prompt(self, original_prompt: str, concept: Dict[str, Any], 
                                  evaluation: Dict[str, Any], project_dir: str = None) -> str:
        """
        Cria um prompt para aprimoramento do conceito.
        
        Args:
            original_prompt (str): Prompt original informado pelo usuário.
            concept (Dict[str, Any]): Conceito original gerado.
            evaluation (Dict[str, Any]): Avaliação do conceito.
            project_dir (str, optional): Diretório do projeto para análise de código.
            
        Returns:
            str: Prompt otimizado para melhorar o conceito.
        """
        self.logger.info("INÍCIO - create_improvement_prompt | Criando prompt para melhorar o conceito")
        
        # Coleta informações sobre os problemas encontrados
        issues = evaluation.get("issues", [])
        issues_str = "- " + "\n- ".join(issues) if issues else "Nenhum problema específico identificado."
        
        # Criar um prompt otimizado
        prompt = f"""
        ### INSTRUÇÕES PARA APRIMORAMENTO DE CONCEITO DE FEATURE ###
        
        Você está revisando um conceito de feature gerado automaticamente que precisa ser aprimorado.
        O objetivo é criar um conceito com fluxo determinístico claro e detalhado.
        
        ### PROMPT ORIGINAL DO USUÁRIO ###
        {original_prompt}
        
        ### CONCEITO ATUAL (NECESSITA MELHORIAS) ###
        ```json
        {json.dumps(concept, indent=2, ensure_ascii=False)}
        ```
        
        ### PROBLEMAS IDENTIFICADOS ###
        {issues_str}
        
        ### REQUISITOS PARA O CONCEITO APRIMORADO ###
        
        1. O "execution_plan" deve conter uma lista detalhada de passos sequenciais e numerados.
        2. Cada passo deve ser específico e descrever claramente uma ação a ser tomada.
        3. O plano deve especificar dados de entrada e saída entre etapas quando relevante.
        4. As etapas devem ter uma ordem clara de execução.
        5. Substitua elementos genéricos ("o sistema deve funcionar") por descrições específicas.
        6. Inclua requisitos técnicos claros quando pertinentes.
        7. A descrição deve detalhar o problema e a solução, não apenas repetir o título.
        
        Forneça sua resposta no formato JSON contendo os mesmos campos do conceito original, porém aprimorados.
        Não inclua explicações fora da estrutura JSON.
        """
        
        # Se tivermos acesso ao diretório do projeto, incluir informações sobre os arquivos
        if project_dir:
            try:
                # Listar arquivos de código-fonte no projeto
                source_files = self.list_source_files(project_dir)
                
                # Limitar a 10 arquivos para não sobrecarregar o prompt
                if len(source_files) > 10:
                    self.logger.info(f"Limitando análise aos 10 arquivos mais relevantes entre {len(source_files)}")
                    # Aqui poderíamos implementar alguma heurística para escolher os mais relevantes
                    # Por enquanto, pegamos apenas os 10 primeiros
                    source_files = source_files[:10]
                
                # Se temos arquivos, incluir informações sobre eles
                if source_files:
                    files_str = "- " + "\n- ".join(source_files)
                    prompt += f"""
                    
                    ### ARQUIVOS RELEVANTES NO PROJETO ###
                    {files_str}
                    
                    ### CONTEÚDO DE ARQUIVOS SELECIONADOS ###
                    """
                    
                    # Adicionar conteúdo de até 3 arquivos para contexto
                    for i, file_path in enumerate(source_files[:3]):
                        file_content = self.read_file_content(project_dir, file_path)
                        # Limitar o tamanho do conteúdo para não exceder limites do modelo
                        content_preview = file_content[:3000] + "..." if len(file_content) > 3000 else file_content
                        prompt += f"\n**{file_path}**\n```\n{content_preview}\n```\n"
            
            except Exception as e:
                self.logger.error(f"Erro ao analisar arquivos do projeto: {str(e)}")
                # Continuar mesmo sem informações do projeto
                
        self.logger.info("FIM - create_improvement_prompt | Prompt criado com sucesso")
        return prompt.strip()

    @log_execution
    def improve_concept(self, concept_id: str, original_prompt: str, evaluation: Dict[str, Any], 
                         project_dir: str = None, elevation_model: str = None) -> Dict[str, Any]:
        """
        Melhora um conceito existente baseado na avaliação.
        
        Args:
            concept_id (str): ID do conceito a ser melhorado.
            original_prompt (str): Prompt original informado pelo usuário.
            evaluation (Dict[str, Any]): Resultado da avaliação do conceito.
            project_dir (str, optional): Diretório do projeto para análise.
            elevation_model (str, optional): Modelo de elevação para usar em vez do padrão.
            
        Returns:
            Dict[str, Any]: Conceito melhorado.
        """
        self.logger.info(f"INÍCIO - improve_concept | Concept ID: {concept_id}")
        
        # Carrega o conceito original
        concept_data = self.load_context(concept_id)
        if not concept_data:
            error_msg = f"Conceito não encontrado para o ID: {concept_id}"
            self.logger.error(error_msg)
            return {"error": error_msg}
        
        # Extrai o conceito (pode estar dentro de um wrapper ou diretamente)
        concept = concept_data.get("concept", concept_data)
        
        # Verificar se temos token da OpenAI
        if not self.openai_token:
            error_msg = "Token OpenAI ausente. Não é possível melhorar o conceito."
            self.logger.error(error_msg)
            return {
                "error": error_msg,
                "original_concept": concept
            }
        
        try:
            # Criar prompt para melhoria
            improvement_prompt = self.create_improvement_prompt(
                original_prompt, concept, evaluation, project_dir
            )
            
            # Configurar cliente da OpenAI
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_token)
            
            # Usar modelo de elevação se fornecido
            model_to_use = elevation_model or self.model
            self.logger.info(f"Usando modelo {model_to_use} para melhoria do conceito")
            
            # Gerar conceito melhorado
            response = client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em melhorar conceitos de features para desenvolvimento de software, garantindo que tenham um fluxo determinístico claro."},
                    {"role": "user", "content": improvement_prompt}
                ],
                temperature=0.5,  # Menor temperatura para respostas mais determinísticas
                max_tokens=4000
            )
            
            improved_concept_text = response.choices[0].message.content.strip()
            
            # Extrair apenas o JSON - caso haja texto explicativo em torno dele
            json_start = improved_concept_text.find('{')
            json_end = improved_concept_text.rfind('}')
            
            if json_start >= 0 and json_end >= 0:
                improved_concept_text = improved_concept_text[json_start:json_end+1]
                
            # Converter para objeto
            try:
                improved_concept = json.loads(improved_concept_text)
                
                # Validar campos mínimos
                required_fields = ["branch_type", "issue_title", "issue_description", "execution_plan"]
                if not all(field in improved_concept for field in required_fields):
                    missing = [f for f in required_fields if f not in improved_concept]
                    self.logger.warning(f"Conceito melhorado falta campos obrigatórios: {missing}")
                
                # Salvar conceito no contexto
                improved_concept_id = self._save_improved_concept(improved_concept, concept_id, original_prompt)
                
                # Avaliar o conceito melhorado
                new_evaluation = self.evaluate_concept(improved_concept)
                
                # Retornar resultado
                return {
                    "improved_concept": improved_concept,
                    "improved_concept_id": improved_concept_id,
                    "original_concept_id": concept_id,
                    "evaluation": new_evaluation
                }
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Resposta não é um JSON válido: {str(e)}")
                return {
                    "error": "Falha ao decodificar JSON do conceito melhorado",
                    "raw_content": improved_concept_text,
                    "original_concept_id": concept_id
                }
                
        except Exception as e:
            self.logger.error(f"FALHA - improve_concept | Erro: {str(e)}", exc_info=True)
            return {
                "error": f"Erro ao melhorar conceito: {str(e)}",
                "original_concept_id": concept_id
            }

    def _save_improved_concept(self, improved_concept: Dict[str, Any], original_concept_id: str, 
                               original_prompt: str) -> str:
        """
        Salva o conceito melhorado no sistema de contexto.
        
        Args:
            improved_concept (Dict[str, Any]): Conceito melhorado.
            original_concept_id (str): ID do conceito original.
            original_prompt (str): Prompt original do usuário.
            
        Returns:
            str: ID do conceito melhorado no sistema de contexto.
        """
        try:
            self.logger.info(f"INÍCIO - _save_improved_concept | Original ID: {original_concept_id}")
            
            # Criar timestamp para o ID do conceito melhorado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            improved_concept_id = f"improved_concept_{timestamp}"
            
            # Preparar dados de contexto
            context_data = {
                "id": improved_concept_id,
                "original_concept_id": original_concept_id,
                "timestamp": datetime.now().isoformat(),
                "prompt": original_prompt,
                "concept": improved_concept,
                "status": "improved_by_guardrail",
                "type": "improved_concept"
            }
            
            # Salvar no arquivo de contexto
            filepath = self.context_dir / f"{improved_concept_id}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Conceito melhorado salvo em: {filepath}")
            
            return improved_concept_id
            
        except Exception as e:
            self.logger.error(f"FALHA - _save_improved_concept | Erro: {str(e)}", exc_info=True)
            return ""

    @log_execution
    def execute_concept_guardrail(self, concept_id: str, prompt: str, project_dir: str = None, 
                                  elevation_model: str = None, force: bool = False) -> Dict[str, Any]:
        """
        Função principal do guardrail para conceitos.
        Avalia, e se necessário, melhora o conceito.
        
        Args:
            concept_id (str): ID do conceito a avaliar.
            prompt (str): Prompt original informado pelo usuário.
            project_dir (str, optional): Caminho para o diretório do projeto.
            elevation_model (str, optional): Modelo alternativo a usar em caso de melhoria.
            force (bool, optional): Se True, ignora a validação e passa o conceito adiante.
            
        Returns:
            Dict[str, Any]: Resultado da execução do guardrail.
        """
        # Iniciar rastreamento
        current_memory_snapshot, peak_memory_snapshot = tracemalloc.get_traced_memory()
        start_time = time.time()
        self.logger.info(f"INÍCIO - execute_concept_guardrail | Memória inicial: {current_memory_snapshot / 1024:.2f} KB")
        
        try:
            # Se force=True, simplesmente passamos o conceito adiante sem validação
            if force:
                self.logger.info("Modo force ativado. Ignorando validação do conceito.")
                concept_data = self.load_context(concept_id)
                if not concept_data:
                    return {"error": f"Conceito não encontrado para o ID: {concept_id}", "force_mode": True}
                
                return {
                    "force_mode": True,
                    "message": "Conceito passado sem validação (modo force ativado)",
                    "concept_id": concept_id,
                    "concept": concept_data
                }
            
            # Carrega o conceito
            concept_data = self.load_context(concept_id)
            if not concept_data:
                self.logger.error(f"Conceito não encontrado para o ID: {concept_id}")
                return {"error": f"Conceito não encontrado para o ID: {concept_id}"}
            
            # Extrai o conceito (pode estar dentro de um wrapper ou diretamente)
            concept = concept_data.get("concept", concept_data)
            
            # Avalia o conceito existente
            evaluation = self.evaluate_concept(concept)
            self.logger.info(f"Avaliação de conceito: Pontuação={evaluation['score']}/10, " +
                            f"Válido={evaluation['is_valid']}, Precisa melhorias={evaluation['needs_improvement']}")
            
            result = {
                "original_concept_id": concept_id,
                "evaluation": evaluation,
                "concept": concept
            }
            
            # Se os conceitos precisam ser melhorados, tenta melhorá-los
            if evaluation["needs_improvement"] or not evaluation["is_valid"]:
                self.logger.info("O conceito precisa de melhorias. Tentando melhorar...")
                
                if not self.openai_token:
                    self.logger.warning("Token OpenAI ausente. Não é possível melhorar o conceito.")
                    result["warning"] = "Token OpenAI ausente. Não foi possível melhorar o conceito."
                    return result
                
                # Melhora o conceito
                improvement_result = self.improve_concept(
                    concept_id, prompt, evaluation, project_dir, elevation_model
                )
                
                # Verifica se houve erro na melhoria
                if "error" in improvement_result:
                    result["error"] = improvement_result["error"]
                    if "raw_content" in improvement_result:
                        result["raw_content"] = improvement_result["raw_content"]
                    return result
                
                # Atualiza o resultado com as informações do conceito melhorado
                result["improved_concept_id"] = improvement_result.get("improved_concept_id")
                result["concept"] = improvement_result.get("improved_concept")
                result["was_improved"] = True
                
                # Avaliar o conceito melhorado novamente para verificar melhoria
                if "evaluation" in improvement_result:
                    result["improved_evaluation"] = improvement_result["evaluation"]
                
                return result
            else:
                # Se o conceito já é bom, apenas retorna o resultado
                result["message"] = "O conceito existente é adequado. Nenhuma melhoria necessária."
                result["was_improved"] = False
                
                return result
                
        except Exception as e:
            self.logger.error(f"FALHA - execute_concept_guardrail | Erro: {str(e)}", exc_info=True)
            return {
                "error": f"Erro ao executar o guardrail do conceito: {str(e)}",
                "concept_id": concept_id
            }
        finally:
            # Finalizar rastreamento
            end_time = time.time()
            current_memory_snapshot, peak_memory_snapshot = tracemalloc.get_traced_memory()
            self.logger.info(f"FIM - execute_concept_guardrail | Tempo: {end_time - start_time:.2f}s | " +
                           f"Pico de memória: {peak_memory_snapshot / 1024:.2f} KB")
    
    @log_execution
    def get_concept_by_id(self, context_id: str) -> Dict[str, Any]:
        """
        Recupera um conceito pelo ID.
        
        Args:
            context_id (str): ID do conceito a recuperar.
            
        Returns:
            Dict[str, Any]: Conceito recuperado ou dicionário vazio se não encontrado.
        """
        return self.load_context(context_id) 