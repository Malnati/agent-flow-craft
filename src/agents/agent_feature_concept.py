import json
import os
import logging
import time
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from core.logger import get_logger, log_execution
from core.utils import mask_sensitive_data

class FeatureConceptAgent:
    """
    Agente responsável por transformar conceitos iniciais em estruturas detalhadas de feature_concept.
    Este agente recebe um conceito gerado pelo ConceptGenerationAgent e o enriquece com informações
    adicionais necessárias para o desenvolvimento da feature.
    """
    
    def __init__(self, openai_token=None, model="gpt-4"):
        self.logger = get_logger(__name__)
        self.logger.info("INÍCIO - FeatureConceptAgent.__init__")
        
        try:
            self.openai_token = openai_token or os.environ.get('OPENAI_API_KEY', '')
            self.context_dir = Path('agent_context')
            self.context_dir.mkdir(exist_ok=True)
            self.model = model
            
            token_available = "disponível" if self.openai_token else "ausente"
            self.logger.debug(f"Status do token OpenAI: {token_available}")
            
            self.logger.info(f"Modelo OpenAI configurado: {self.model}")
            
            if not self.openai_token:
                self.logger.warning("ALERTA - Token OpenAI ausente | Funcionalidades limitadas")
            
            self.logger.info("SUCESSO - FeatureConceptAgent inicializado")
            
        except Exception as e:
            # Mascarar possíveis tokens na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            self.logger.error(f"FALHA - FeatureConceptAgent.__init__ | Erro: {error_msg}", exc_info=True)
            raise
    
    def set_model(self, model):
        """
        Define o modelo da OpenAI a ser utilizado.
        
        Args:
            model (str): Nome do modelo da OpenAI (ex: gpt-3.5-turbo, gpt-4)
        """
        self.logger.info(f"INÍCIO - set_model | Modelo anterior: {self.model} | Novo modelo: {model}")
        self.model = model
        self.logger.info(f"SUCESSO - Modelo alterado para: {self.model}")
        return self.model
    
    @log_execution
    def process_concept(self, concept_id, project_dir=None):
        """
        Processa um conceito gerado pelo ConceptGenerationAgent transformando-o em um feature_concept enriquecido.
        
        Args:
            concept_id (str): ID do contexto do conceito a ser processado
            project_dir (str): Diretório do projeto para análise de contexto (opcional)
            
        Returns:
            dict: Feature concept gerado com informações enriquecidas
        """
        self.logger.info(f"INÍCIO - process_concept | Concept ID: {concept_id}")
        
        try:
            # Carregar o conceito original
            concept_data = self._load_concept_from_context(concept_id)
            if not concept_data or "concept" not in concept_data:
                raise ValueError(f"Conceito não encontrado ou inválido: {concept_id}")
            
            original_concept = concept_data["concept"]
            original_prompt = concept_data.get("prompt", "")
            
            if not self.openai_token:
                self.logger.error("Token OpenAI ausente")
                feature_concept = self._create_default_feature_concept(original_concept, original_prompt)
                context_id = self._save_feature_concept_to_context(feature_concept, original_prompt, concept_id)
                feature_concept["context_id"] = context_id
                return feature_concept
                
            client = OpenAI(api_key=self.openai_token)
            
            # Analisar contexto adicional do projeto
            project_context = ""
            if project_dir:
                project_context = self._analyze_project_context(project_dir)
            
            # Enviar para a API para enriquecer o conceito
            context = f"""
            Você é especialista em transformar conceitos de software em especificações detalhadas.
            
            Conceito original:
            {json.dumps(original_concept, indent=2)}
            
            Contexto do projeto:
            {project_context or "Contexto do projeto não disponível"}
            
            Sua tarefa é enriquecer este conceito, adicionando detalhes técnicos e definições mais precisas.
            
            Retorne sua resposta no seguinte formato JSON (sem texto adicional):
            {{
                "branch_type": "tipo de branch (feat, fix, docs, chore, etc)",
                "issue_title": "título claro e conciso para a issue",
                "issue_description": "descrição detalhada sobre o que deve ser implementado",
                "generated_branch_suffix": "sufixo para o nome da branch (usar kebab-case)",
                "execution_plan": {{
                    "steps": [
                        "lista de passos de implementação"
                    ],
                    "estimated_complexity": "baixa|média|alta",
                    "estimated_hours": "estimativa em horas",
                    "technical_details": "detalhes técnicos da implementação",
                    "dependencies": [
                        "dependências externas necessárias"
                    ],
                    "affected_components": [
                        "componentes do sistema afetados"
                    ]
                }}
            }}
            """
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": f"Enriqueça o seguinte conceito: {original_prompt}"}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            suggestion = response.choices[0].message.content
            
            # Mascarar possíveis dados sensíveis na resposta
            safe_suggestion = mask_sensitive_data(suggestion[:100])
            self.logger.info(f"Sugestão recebida do OpenAI: {safe_suggestion}...")
            
            # Garantir que a resposta é um JSON válido
            try:
                feature_concept = json.loads(suggestion)
                self.logger.debug("Feature concept convertido com sucesso para JSON")
                # Adicionar a referência ao conceito original
                feature_concept["original_concept_id"] = concept_id
                # Salvar e obter o ID do contexto
                context_id = self._save_feature_concept_to_context(feature_concept, original_prompt, concept_id)
                # Adicionar o context_id ao feature concept retornado
                feature_concept["context_id"] = context_id
                return feature_concept
                
            except json.JSONDecodeError:
                self.logger.warning(f"Resposta não é um JSON válido. Criando JSON padrão.")
                feature_concept = self._create_default_feature_concept(original_concept, original_prompt)
                context_id = self._save_feature_concept_to_context(feature_concept, original_prompt, concept_id, error="formato_json_invalido")
                feature_concept["context_id"] = context_id
                return feature_concept
                
        except Exception as e:
            # Mascarar possíveis tokens na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            self.logger.error(f"FALHA - process_concept | Erro: {error_msg}", exc_info=True)
            if 'original_concept' in locals():
                feature_concept = self._create_default_feature_concept(original_concept, original_prompt)
            else:
                feature_concept = self._create_default_feature_concept({}, "")
            context_id = self._save_feature_concept_to_context(feature_concept, original_prompt if 'original_prompt' in locals() else "", concept_id, error=str(e))
            feature_concept["context_id"] = context_id
            return feature_concept
        finally:
            self.logger.info("FIM - process_concept")
    
    def _analyze_project_context(self, project_dir):
        """
        Analisa o contexto do projeto para obter informações relevantes.
        
        Args:
            project_dir (str): Diretório do projeto
            
        Returns:
            str: Contexto do projeto em formato texto
        """
        try:
            project_path = Path(project_dir)
            if not project_path.exists():
                return "Diretório do projeto não encontrado"
                
            # Análise simples do projeto (pode ser expandida conforme necessário)
            readme_files = list(project_path.glob("**/README*"))
            package_files = list(project_path.glob("**/package.json")) + list(project_path.glob("**/pyproject.toml"))
            
            context = []
            
            # Extrair informações de README
            for readme in readme_files[:1]:  # Limitar a 1 arquivo README para não sobrecarregar
                try:
                    with open(readme, 'r', encoding='utf-8') as f:
                        content = f.read()
                        context.append(f"README: {content[:500]}...")  # Primeiros 500 caracteres
                except Exception:
                    pass
            
            # Extrair informações de package.json ou pyproject.toml
            for pkg in package_files[:1]:  # Limitar a 1 arquivo de dependências
                try:
                    with open(pkg, 'r', encoding='utf-8') as f:
                        content = f.read()
                        context.append(f"Dependências ({pkg.name}): {content[:500]}...")  # Primeiros 500 caracteres
                except Exception:
                    pass
            
            return "\n\n".join(context) if context else "Não foi possível extrair contexto do projeto"
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar contexto do projeto: {str(e)}", exc_info=True)
            return "Erro ao analisar contexto do projeto"
    
    def _create_default_feature_concept(self, original_concept, prompt_text):
        """
        Cria um feature concept padrão quando ocorrem falhas.
        
        Args:
            original_concept (dict): Conceito original
            prompt_text (str): Descrição da feature original
            
        Returns:
            dict: Feature concept padrão
        """
        # Usar informações do conceito original quando disponíveis
        branch_type = original_concept.get("branch_type", "feat")
        issue_title = original_concept.get("issue_title", f"Feature: {prompt_text}")
        issue_description = original_concept.get("issue_description", prompt_text)
        branch_suffix = original_concept.get("generated_branch_suffix", "")
        
        # Se não houver sufixo, normalizar prompt para branch_suffix
        if not branch_suffix:
            suffix = prompt_text.lower().replace(" ", "-")
            if suffix.startswith("implementar-"):
                branch_suffix = suffix[:30]
            else:
                branch_suffix = "implementar-" + suffix[:20]
        
        # Criar um plano de execução mais detalhado
        execution_plan = {
            "steps": original_concept.get("execution_plan", {}).get("steps", [
                "1. Análise dos requisitos",
                "2. Desenvolvimento da solução",
                "3. Criação de testes",
                "4. Documentação"
            ]),
            "estimated_complexity": "média",
            "estimated_hours": "4-8",
            "technical_details": "Implementação básica conforme solicitado no prompt",
            "dependencies": [],
            "affected_components": []
        }
            
        return {
            "branch_type": branch_type,
            "issue_title": issue_title,
            "issue_description": issue_description,
            "generated_branch_suffix": branch_suffix,
            "execution_plan": execution_plan
        }
    
    def _load_concept_from_context(self, context_id):
        """
        Carrega um conceito do sistema de contexto.
        
        Args:
            context_id (str): ID do contexto a ser carregado
            
        Returns:
            dict: Dados do contexto ou None se não encontrado
        """
        try:
            context_file = self.context_dir / f"{context_id}.json"
            if not context_file.exists():
                self.logger.error(f"Arquivo de contexto não encontrado: {context_file}")
                return None
                
            with open(context_file, 'r', encoding='utf-8') as f:
                context_data = json.load(f)
                
            self.logger.info(f"Contexto carregado com sucesso de {context_file}")
            return context_data
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar contexto: {str(e)}", exc_info=True)
            return None
    
    def _save_feature_concept_to_context(self, feature_concept, prompt_text, original_concept_id, error=None):
        """
        Salva o feature concept gerado em arquivo JSON para transferência entre agentes.
        
        Args:
            feature_concept (dict): Feature concept gerado
            prompt_text (str): Prompt original
            original_concept_id (str): ID do conceito original
            error (str): Erro ocorrido, se houver
            
        Returns:
            str: ID do contexto criado
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            context_id = f"feature_concept_{timestamp}"
            context_file = self.context_dir / f"{context_id}.json"
            
            self.logger.info(f"Tentando salvar feature concept em: {context_file}")
            
            # Garantir que o diretório de contexto exista
            if not self.context_dir.exists():
                self.logger.info(f"Diretório não existe, criando: {self.context_dir}")
                self.context_dir.mkdir(parents=True, exist_ok=True)
            
            context_data = {
                "id": context_id,
                "type": "feature_concept",
                "timestamp": timestamp,
                "prompt": prompt_text,
                "original_concept_id": original_concept_id,
                "feature_concept": feature_concept,
                "status": "error" if error else "success",
                "error": error
            }
            
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, indent=2)
                
            self.logger.info(f"Feature concept salvo com sucesso em {context_file}")
            return context_id
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar feature concept: {str(e)}", exc_info=True)
            return None

    @log_execution
    def get_feature_concept_by_id(self, context_id):
        """
        Recupera um feature concept pelo ID do contexto.
        
        Args:
            context_id (str): ID do contexto a ser recuperado
            
        Returns:
            dict: Feature concept ou None se não encontrado
        """
        try:
            context_data = self._load_concept_from_context(context_id)
            if not context_data or "feature_concept" not in context_data:
                self.logger.error(f"Feature concept não encontrado ou inválido: {context_id}")
                return None
                
            return context_data["feature_concept"]
            
        except Exception as e:
            self.logger.error(f"Erro ao recuperar feature concept: {str(e)}", exc_info=True)
            return None 