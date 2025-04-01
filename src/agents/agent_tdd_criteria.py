#!/usr/bin/env python3
"""
TDDCriteriaAgent: Agente responsável por gerar critérios de aceitação TDD para features.

Este agente gera um prompt otimizado para o modelo OpenAI que inclui:
- O conceito JSON gerado anteriormente
- Listagem de arquivos de código-fonte do repositório alvo
- Conteúdo dos arquivos de código-fonte relevantes

O objetivo é obter uma lista de critérios de aceitação TDD para a implementação
da feature descrita no prompt inicial, baseado no contexto do repositório.
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
    from core.logger import get_logger, log_execution
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
    from core.utils import mask_sensitive_data
    has_utils = True
except ImportError:
    has_utils = False
    def mask_sensitive_data(data, mask_str='***'):
        if isinstance(data, str) and any(s in data.lower() for s in ['token', 'key', 'secret', 'password']):
            if len(data) > 10:
                return f"{data[:4]}{'*' * 12}{data[-4:] if len(data) > 8 else ''}"
            return mask_str
        return data

class TDDCriteriaAgent:
    """
    Agente responsável por gerar critérios de aceitação TDD para features.
    
    Este agente utiliza o modelo OpenAI para analisar o conceito da feature e o código-fonte
    do repositório alvo, gerando uma lista de critérios de aceitação TDD relevantes para
    a implementação da feature.
    """
    
    def __init__(self, openai_token=None, model="gpt-4-turbo"):
        """
        Inicializa o agente TDDCriteriaAgent.
        
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
    def load_concept(self, context_id: str) -> Dict[str, Any]:
        """
        Carrega um conceito de feature pelo ID do contexto.
        
        Args:
            context_id (str): ID do contexto a ser carregado.
            
        Returns:
            Dict[str, Any]: Dados do conceito carregado, ou dicionário vazio se não encontrado.
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
            self.logger.error(f"FALHA - load_concept | Erro ao carregar conceito: {str(e)}", exc_info=True)
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
    def generate_prompt(self, concept_data: Dict[str, Any], project_dir: str, max_files: int = 10) -> str:
        """
        Gera o prompt para o modelo OpenAI com o conceito e informações do projeto.
        
        Args:
            concept_data (Dict[str, Any]): Dados do conceito da feature.
            project_dir (str): Caminho para o diretório do projeto.
            max_files (int, optional): Número máximo de arquivos a incluir. Padrão é 10.
            
        Returns:
            str: Prompt formatado para envio ao modelo.
        """
        # Extrai informações relevantes do conceito
        prompt_text = concept_data.get("prompt", "")
        concept = concept_data.get("concept", {})
        
        # Monta o cabeçalho do prompt
        prompt = f"""# Geração de Critérios de Aceitação TDD

## Descrição da Feature
{prompt_text}

## Conceito da Feature
```json
{json.dumps(concept, indent=2, ensure_ascii=False)}
```

"""
        
        # Lista arquivos do projeto
        files = self.list_source_files(project_dir)
        
        # Adiciona listagem de arquivos ao prompt
        prompt += "\n## Arquivos do Projeto\n"
        for file in files[:max_files]:
            prompt += f"- {file}\n"
            
        # Se houver muitos arquivos, indica que há mais
        if len(files) > max_files:
            prompt += f"\n... e mais {len(files) - max_files} arquivos\n"
            
        # Adiciona conteúdo de alguns arquivos relevantes
        # Heurística simples: arquivos que podem ter relação com o título da issue
        issue_title = concept.get("issue_title", "").lower()
        keywords = [word for word in issue_title.split() if len(word) > 3]
        
        # Seleciona arquivos que contêm palavras-chave no caminho
        relevant_files = [
            file for file in files
            if any(keyword in file.lower() for keyword in keywords)
        ]
        
        # Se não encontrou arquivos relevantes, usa os primeiros da lista
        if not relevant_files and files:
            relevant_files = files[:min(5, len(files))]
            
        # Adiciona conteúdo dos arquivos relevantes
        prompt += "\n## Conteúdo de Arquivos Relevantes\n"
        
        for file in relevant_files[:5]:  # Limita a 5 arquivos para não exceder limites de tokens
            content = self.read_file_content(project_dir, file)
            if content:
                prompt += f"\n### Arquivo: {file}\n```\n{content[:2000]}```\n"
                if len(content) > 2000:
                    prompt += "\n... (conteúdo truncado) ...\n"
                    
        # Adiciona instruções para o modelo
        prompt += """
## Instruções
Com base no conceito da feature e nos arquivos do projeto, gere uma lista completa de critérios de aceitação TDD.
Cada critério deve:

1. Ser específico e testável
2. Cobrir casos de uso principais e de borda
3. Seguir o formato "DADO... QUANDO... ENTÃO..."
4. Ser organizado por componente ou funcionalidade

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
      "edge_cases": ["caso de borda 1", "caso de borda 2"]
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
    def generate_tdd_criteria(self, context_id: str, project_dir: str) -> Dict[str, Any]:
        """
        Gera critérios de aceitação TDD baseados no conceito e contexto do projeto.
        
        Args:
            context_id (str): ID do contexto do conceito de feature.
            project_dir (str): Caminho para o diretório do projeto.
            
        Returns:
            Dict[str, Any]: Critérios de aceitação TDD gerados, ou dicionário com erro.
        """
        try:
            # Verifica se tem token OpenAI
            if not self.openai_token:
                self.logger.warning("Token OpenAI ausente. Usando critérios padrão.")
                default_criteria = self._create_default_criteria()
                
                # Adiciona metadados aos critérios padrão
                default_criteria["context_id"] = context_id
                
                # Salva os critérios padrão no diretório de contexto
                criteria_id = f"tdd_criteria_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self._save_criteria_to_context(criteria_id, default_criteria, context_id)
                
                return default_criteria
                
            # Carrega o conceito pelo context_id
            concept_data = self.load_concept(context_id)
            if not concept_data:
                self.logger.error(f"Conceito não encontrado para o ID: {context_id}")
                return {"error": f"Conceito não encontrado para o ID: {context_id}"}
                
            # Gera o prompt para o modelo
            prompt = self.generate_prompt(concept_data, project_dir)
            
            # Configura o cliente OpenAI
            openai.api_key = self.openai_token
            
            # Solicita os critérios TDD ao modelo
            self.logger.info(f"Enviando solicitação à API OpenAI (modelo: {self.model})...")
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um especialista em Test-Driven Development que gera critérios de aceitação detalhados para novas features."},
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
                    tdd_criteria = json.loads(json_str)
                    # Adiciona metadados
                    tdd_criteria["context_id"] = context_id
                    tdd_criteria["generated_at"] = datetime.now().isoformat()
                    tdd_criteria["model_used"] = self.model
                    
                    # Salva os critérios no diretório de contexto
                    criteria_id = f"tdd_criteria_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    self._save_criteria_to_context(criteria_id, tdd_criteria, context_id)
                    
                    return tdd_criteria
                except json.JSONDecodeError as e:
                    self.logger.error(f"FALHA - Erro ao decodificar JSON: {str(e)}")
                    # Retorna texto bruto se falhar ao decodificar JSON
                    return {
                        "error": "Formato JSON inválido",
                        "raw_content": answer,
                        "context_id": context_id
                    }
            else:
                # Se não conseguir extrair JSON, retorna o texto completo
                return {
                    "raw_content": answer,
                    "context_id": context_id,
                    "generated_at": datetime.now().isoformat(),
                    "model_used": self.model
                }
                
        except Exception as e:
            self.logger.error(f"FALHA - generate_tdd_criteria | Erro: {str(e)}", exc_info=True)
            return {
                "error": f"Erro ao gerar critérios TDD: {str(e)}",
                "context_id": context_id
            }
    
    def _create_default_criteria(self) -> Dict[str, Any]:
        """
        Cria critérios de aceitação TDD padrão quando ocorrem falhas.
        
        Returns:
            Dict[str, Any]: Critérios de aceitação TDD padrão.
        """
        return {
            "criteria": [
                {
                    "id": "TDD-001",
                    "component": "Core",
                    "description": "Verificar funcionalidade básica",
                    "given": "Usuário autenticado no sistema",
                    "when": "Usuário interage com a nova funcionalidade",
                    "then": "Sistema deve responder conforme esperado",
                    "edge_cases": ["Entrada inválida", "Timeout"]
                },
                {
                    "id": "TDD-002",
                    "component": "UI",
                    "description": "Verificar elementos de interface",
                    "given": "Interface carregada",
                    "when": "Usuário visualiza os componentes",
                    "then": "Todos os elementos devem estar visíveis e funcionais",
                    "edge_cases": ["Tela pequena", "Tema escuro"]
                }
            ],
            "test_plan": {
                "unit_tests": [
                    "Teste unitário para validação de entrada",
                    "Teste unitário para processamento de dados"
                ],
                "integration_tests": [
                    "Teste de integração entre módulos relacionados"
                ],
                "e2e_tests": [
                    "Teste de ponta a ponta do fluxo principal do usuário"
                ]
            },
            "generated_at": datetime.now().isoformat(),
            "source": "default_template",
            "note": "Critérios gerados automaticamente. Sugerimos personalizar para sua feature específica."
        }
    
    @log_execution
    def _save_criteria_to_context(self, criteria_id: str, criteria: Dict[str, Any], concept_id: str) -> str:
        """
        Salva os critérios de aceitação TDD no diretório de contexto.
        
        Args:
            criteria_id (str): ID único para os critérios.
            criteria (Dict[str, Any]): Critérios de aceitação TDD a serem salvos.
            concept_id (str): ID do contexto do conceito relacionado.
            
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
                "type": "tdd_criteria",
                "concept_id": concept_id,
                "created_at": datetime.now().isoformat(),
                "criteria": criteria
            }
            
            # Salva o arquivo
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Critérios TDD salvos em: {context_file}")
            return criteria_id
            
        except Exception as e:
            self.logger.error(f"FALHA - _save_criteria_to_context | Erro: {str(e)}", exc_info=True)
            return ""
    
    @log_execution 
    def get_criteria_by_id(self, criteria_id: str) -> Dict[str, Any]:
        """
        Recupera critérios TDD pelo ID.
        
        Args:
            criteria_id (str): ID dos critérios a serem recuperados.
            
        Returns:
            Dict[str, Any]: Critérios recuperados, ou dicionário vazio se não encontrado.
        """
        try:
            # Tenta localizar o arquivo de contexto correspondente
            context_file = self.context_dir / f"{criteria_id}.json"
            
            if not context_file.exists():
                self.logger.warning(f"Arquivo de critérios não encontrado: {context_file}")
                return {}
            
            # Carrega o arquivo JSON
            with open(context_file, 'r', encoding='utf-8') as f:
                criteria_data = json.load(f)
                
            self.logger.info(f"Critérios carregados com sucesso: {criteria_id}")
            return criteria_data
        except Exception as e:
            self.logger.error(f"FALHA - get_criteria_by_id | Erro: {str(e)}", exc_info=True)
            return {} 