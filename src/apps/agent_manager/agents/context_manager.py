import json
import os
import time
from datetime import datetime
from pathlib import Path
from core.core.logger import get_logger, log_execution

class ContextManager:
    """
    Gerenciador de contexto para facilitar a transferência de dados entre agentes.
    Cria, armazena e recupera arquivos de contexto no formato JSON.
    """
    
    def __init__(self, base_dir='agent_context'):
        self.logger = get_logger(__name__)
        self.logger.info(f"INÍCIO - ContextManager.__init__ | Base dir: {base_dir}")
        
        try:
            self.base_dir = Path(base_dir)
            self.base_dir.mkdir(exist_ok=True)
            self.logger.info(f"SUCESSO - ContextManager inicializado | Diretório: {self.base_dir}")
        except Exception as e:
            self.logger.error(f"FALHA - ContextManager.__init__ | Erro: {str(e)}", exc_info=True)
            raise
    
    @log_execution
    def create_context(self, data, context_type='default'):
        """
        Cria um novo arquivo de contexto.
        
        Args:
            data (dict): Dados a serem armazenados no contexto
            context_type (str): Tipo de contexto para prefixar o nome do arquivo
            
        Returns:
            str: ID do contexto criado
        """
        self.logger.info(f"INÍCIO - create_context | Tipo: {context_type}")
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            context_id = f"{context_type}_{timestamp}"
            
            # Adicionar metadados ao contexto
            context_data = {
                "id": context_id,
                "type": context_type,
                "timestamp": timestamp,
                "created_at": datetime.now().isoformat(),
                "data": data
            }
            
            context_file = self.base_dir / f"{context_id}.json"
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, indent=2)
                
            self.logger.info(f"SUCESSO - Contexto criado | ID: {context_id}, Arquivo: {context_file}")
            return context_id
            
        except Exception as e:
            self.logger.error(f"FALHA - create_context | Erro: {str(e)}", exc_info=True)
            return None
    
    @log_execution
    def get_context(self, context_id):
        """
        Recupera um contexto pelo ID.
        
        Args:
            context_id (str): ID do contexto a ser recuperado
            
        Returns:
            dict: Dados do contexto ou None se não encontrado
        """
        self.logger.info(f"INÍCIO - get_context | ID: {context_id}")
        
        try:
            context_file = self.base_dir / f"{context_id}.json"
            if not context_file.exists():
                self.logger.warning(f"Contexto não encontrado | ID: {context_id}")
                return None
                
            with open(context_file, 'r', encoding='utf-8') as f:
                context_data = json.load(f)
                
            self.logger.info(f"SUCESSO - Contexto recuperado | ID: {context_id}")
            return context_data
            
        except Exception as e:
            self.logger.error(f"FALHA - get_context | Erro: {str(e)}", exc_info=True)
            return None
    
    @log_execution
    def update_context(self, context_id, data, merge=True):
        """
        Atualiza um contexto existente.
        
        Args:
            context_id (str): ID do contexto a ser atualizado
            data (dict): Novos dados a serem adicionados/substituídos
            merge (bool): Se True, faz merge com dados existentes; se False, substitui completamente
            
        Returns:
            bool: True se atualização foi bem-sucedida, False caso contrário
        """
        self.logger.info(f"INÍCIO - update_context | ID: {context_id}, Merge: {merge}")
        
        try:
            # Recuperar contexto existente
            context_data = self.get_context(context_id)
            if not context_data:
                self.logger.warning(f"Contexto não encontrado para atualização | ID: {context_id}")
                return False
                
            # Atualizar dados
            if merge:
                if isinstance(context_data.get('data', {}), dict) and isinstance(data, dict):
                    context_data['data'].update(data)
                else:
                    # Se um dos dados não for dict, substituir completamente
                    context_data['data'] = data
            else:
                context_data['data'] = data
                
            # Adicionar metadados de atualização
            context_data['updated_at'] = datetime.now().isoformat()
            
            # Salvar contexto atualizado
            context_file = self.base_dir / f"{context_id}.json"
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, indent=2)
                
            self.logger.info(f"SUCESSO - Contexto atualizado | ID: {context_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"FALHA - update_context | Erro: {str(e)}", exc_info=True)
            return False
    
    @log_execution
    def list_contexts(self, context_type=None, limit=10):
        """
        Lista os contextos disponíveis, opcionalmente filtrados por tipo.
        
        Args:
            context_type (str): Filtrar por tipo de contexto
            limit (int): Número máximo de contextos a retornar
            
        Returns:
            list: Lista de IDs de contexto
        """
        self.logger.info(f"INÍCIO - list_contexts | Tipo: {context_type}, Limite: {limit}")
        
        try:
            # Listar arquivos JSON no diretório de contexto
            context_files = list(self.base_dir.glob("*.json"))
            
            # Ordenar por data de modificação (mais recentes primeiro)
            context_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            contexts = []
            for file_path in context_files[:limit]:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Filtrar por tipo se especificado
                    if context_type and data.get('type') != context_type:
                        continue
                        
                    contexts.append({
                        'id': data.get('id'),
                        'type': data.get('type'),
                        'created_at': data.get('created_at'),
                        'updated_at': data.get('updated_at', data.get('created_at'))
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Erro ao ler arquivo de contexto {file_path}: {str(e)}")
                    
            self.logger.info(f"SUCESSO - Listagem de contextos | Total: {len(contexts)}")
            return contexts
            
        except Exception as e:
            self.logger.error(f"FALHA - list_contexts | Erro: {str(e)}", exc_info=True)
            return []
    
    @log_execution
    def delete_context(self, context_id):
        """
        Remove um contexto pelo ID.
        
        Args:
            context_id (str): ID do contexto a ser removido
            
        Returns:
            bool: True se remoção foi bem-sucedida, False caso contrário
        """
        self.logger.info(f"INÍCIO - delete_context | ID: {context_id}")
        
        try:
            context_file = self.base_dir / f"{context_id}.json"
            if not context_file.exists():
                self.logger.warning(f"Contexto não encontrado para exclusão | ID: {context_id}")
                return False
                
            os.remove(context_file)
            self.logger.info(f"SUCESSO - Contexto removido | ID: {context_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"FALHA - delete_context | Erro: {str(e)}", exc_info=True)
            return False
    
    @log_execution
    def clean_old_contexts(self, days=7):
        """
        Remove contextos mais antigos que X dias.
        
        Args:
            days (int): Número de dias para manter contextos
            
        Returns:
            int: Número de contextos removidos
        """
        self.logger.info(f"INÍCIO - clean_old_contexts | Dias: {days}")
        
        try:
            now = time.time()
            max_age = days * 24 * 60 * 60  # Converter dias para segundos
            
            removed = 0
            for file_path in self.base_dir.glob("*.json"):
                file_age = now - os.path.getmtime(file_path)
                if file_age > max_age:
                    try:
                        os.remove(file_path)
                        removed += 1
                    except Exception as e:
                        self.logger.warning(f"Erro ao remover arquivo antigo {file_path}: {str(e)}")
                        
            self.logger.info(f"SUCESSO - Limpeza de contextos antigos | Removidos: {removed}")
            return removed
            
        except Exception as e:
            self.logger.error(f"FALHA - clean_old_contexts | Erro: {str(e)}", exc_info=True)
            return 0 