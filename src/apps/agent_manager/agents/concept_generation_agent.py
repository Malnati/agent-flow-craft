import json
import os
import logging
import time
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from agent_platform.core.logger import get_logger, log_execution

# Tente importar funções de mascaramento de dados sensíveis
try:
    from agent_platform.core.utils import mask_sensitive_data, get_env_status
    has_utils = True
except ImportError:
    has_utils = False
    # Função básica de fallback para mascaramento
    def mask_sensitive_data(data, mask_str='***'):
        if isinstance(data, str) and any(s in data.lower() for s in ['token', 'key', 'secret', 'password']):
            # Mostrar parte do início e fim para debugging
            if len(data) > 10:
                return f"{data[:4]}{'*' * 12}{data[-4:] if len(data) > 8 else ''}"
            return mask_str
        return data

class ConceptGenerationAgent:
    """
    Agente responsável por gerar conceitos iniciais de features a partir de prompts do usuário.
    Este agente lida apenas com a geração de conceitos básicos do que deve ser implementado,
    utilizando a OpenAI para processar a solicitação do usuário.
    """
    
    def __init__(self, openai_token=None, model="gpt-4"):
        self.logger = get_logger(__name__)
        self.logger.info("INÍCIO - ConceptGenerationAgent.__init__")
        
        try:
            self.openai_token = openai_token or os.environ.get('OPENAI_API_KEY', '')
            self.context_dir = Path('agent_context')
            self.context_dir.mkdir(exist_ok=True)
            self.model = model
            
            # Logar status do token sem expor dados sensíveis
            if has_utils:
                token_status = get_env_status('OPENAI_API_KEY')
                self.logger.debug(f"Status do token OpenAI: {token_status}")
            else:
                token_available = "disponível" if self.openai_token else "ausente"
                self.logger.debug(f"Status do token OpenAI: {token_available}")
            
            self.logger.info(f"Modelo OpenAI configurado: {self.model}")
            
            if not self.openai_token:
                self.logger.warning("ALERTA - Token OpenAI ausente | Funcionalidades limitadas")
            
            self.logger.info("SUCESSO - ConceptGenerationAgent inicializado")
            
        except Exception as e:
            # Mascarar possíveis tokens na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            self.logger.error(f"FALHA - ConceptGenerationAgent.__init__ | Erro: {error_msg}", exc_info=True)
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
    def generate_concept(self, prompt_text, git_log=None):
        """
        Gera um conceito de feature básico baseado no prompt do usuário e contexto do Git.
        
        Args:
            prompt_text (str): Descrição da feature desejada
            git_log (str): Log do Git para contexto (opcional)
            
        Returns:
            dict: Conceito básico gerado
        """
        self.logger.info(f"INÍCIO - generate_concept | Prompt: {prompt_text[:100]}...")
        
        try:
            if not self.openai_token:
                self.logger.error("Token OpenAI ausente")
                concept = self._create_default_concept(prompt_text)
                # Salvar mesmo com erro
                context_id = self._save_concept_to_context(concept, prompt_text, error="token_openai_ausente")
                # Adicionar o context_id ao conceito retornado
                concept["context_id"] = context_id
                return concept
                
            client = OpenAI(api_key=self.openai_token)
            
            context = f"""
            Histórico de commits recentes:
            {git_log or "Histórico Git não disponível"}
            
            Seu papel é entender e conceitualizar uma nova funcionalidade a partir da descrição do usuário.
            
            Retorne sua resposta no seguinte formato JSON (sem texto adicional):
            {{
                "concept_summary": "resumo conciso do conceito proposto",
                "concept_description": "descrição detalhada do conceito",
                "key_goals": ["lista de principais objetivos"],
                "possible_approaches": ["possíveis abordagens para implementação"],
                "considerations": ["considerações importantes sobre a implementação"]
            }}
            """
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": prompt_text}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            suggestion = response.choices[0].message.content
            
            # Mascarar possíveis dados sensíveis na resposta
            safe_suggestion = mask_sensitive_data(suggestion[:100])
            self.logger.info(f"Sugestão recebida do OpenAI: {safe_suggestion}...")
            
            # Garantir que a resposta é um JSON válido
            try:
                concept = json.loads(suggestion)
                self.logger.debug("Conceito convertido com sucesso para JSON")
                # Salvar e obter o ID do contexto
                context_id = self._save_concept_to_context(concept, prompt_text)
                # Adicionar o context_id ao conceito retornado
                concept["context_id"] = context_id
                return concept
                
            except json.JSONDecodeError:
                self.logger.warning(f"Resposta não é um JSON válido. Criando JSON padrão.")
                concept = self._create_default_concept(prompt_text)
                # Salvar mesmo com erro de formato
                context_id = self._save_concept_to_context(concept, prompt_text, error="formato_json_invalido")
                # Adicionar o context_id ao conceito retornado 
                concept["context_id"] = context_id
                return concept
                
        except Exception as e:
            # Mascarar possíveis tokens na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            self.logger.error(f"FALHA - generate_concept | Erro: {error_msg}", exc_info=True)
            concept = self._create_default_concept(prompt_text)
            # Salvar com informação do erro
            context_id = self._save_concept_to_context(concept, prompt_text, error=str(e))
            # Adicionar o context_id ao conceito retornado
            concept["context_id"] = context_id
            return concept
        finally:
            self.logger.info("FIM - generate_concept")
    
    def _create_default_concept(self, prompt_text):
        """
        Cria um conceito padrão quando ocorrem falhas.
        
        Args:
            prompt_text (str): Descrição da feature original
            
        Returns:
            dict: Conceito padrão
        """
        return {
            "concept_summary": prompt_text,
            "concept_description": f"Solicitação original: {prompt_text}",
            "key_goals": ["Implementar a funcionalidade solicitada"],
            "possible_approaches": ["Abordagem direta de implementação"],
            "considerations": ["Validar requisitos com o solicitante"]
        }
    
    def _save_concept_to_context(self, concept, prompt_text, error=None):
        """
        Salva o conceito gerado em arquivo JSON para transferência entre agentes.
        
        Args:
            concept (dict): Conceito gerado
            prompt_text (str): Prompt original
            error (str): Erro ocorrido, se houver
            
        Returns:
            str: ID do contexto criado
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            context_id = f"concept_{timestamp}"
            context_file = self.context_dir / f"{context_id}.json"
            
            self.logger.info(f"Tentando salvar contexto em: {context_file} (diretório: {self.context_dir.resolve()})")
            
            # Garantir que o diretório de contexto exista
            if not self.context_dir.exists():
                self.logger.info(f"Diretório não existe, criando: {self.context_dir}")
                self.context_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Diretório de contexto criado: {self.context_dir}")
            else:
                self.logger.info(f"Diretório já existe: {self.context_dir}")
            
            context_data = {
                "id": context_id,
                "type": "concept",
                "timestamp": timestamp,
                "prompt": prompt_text,
                "concept": concept,
                "status": "error" if error else "success",
                "error": error
            }
            
            self.logger.info(f"Escrevendo arquivo: {context_file}")
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, indent=2)
                
            self.logger.info(f"Contexto salvo com sucesso em {context_file}")
            return context_id
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar contexto: {str(e)}", exc_info=True)
            return None

    @log_execution
    def get_concept_by_id(self, context_id):
        """
        Recupera um conceito pelo ID do contexto.
        
        Args:
            context_id (str): ID do contexto a ser recuperado
            
        Returns:
            dict: Conceito ou None se não encontrado
        """
        try:
            context_file = self.context_dir / f"{context_id}.json"
            if not context_file.exists():
                self.logger.error(f"Arquivo de contexto não encontrado: {context_file}")
                return None
                
            with open(context_file, 'r', encoding='utf-8') as f:
                context_data = json.load(f)
                
            if "concept" not in context_data:
                self.logger.error(f"Conceito não encontrado no contexto: {context_id}")
                return None
                
            self.logger.info(f"Conceito recuperado com sucesso: {context_id}")
            return context_data["concept"]
            
        except Exception as e:
            self.logger.error(f"Erro ao recuperar conceito: {str(e)}", exc_info=True)
            return None 