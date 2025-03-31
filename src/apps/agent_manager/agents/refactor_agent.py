"""
Agente para refatorar código Python usando a biblioteca Rope.
Este agente identifica oportunidades de refatoração e as aplica automaticamente.
"""
import os
import re
import sys
import logging
import time
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Set, Union

import rope.base.project
from rope.base.project import Project
from rope.base import libutils, exceptions
from rope.refactor.rename import Rename
from rope.refactor.extract import ExtractMethod, ExtractVariable
from rope.refactor.move import MoveMethod, MoveGlobal
from rope.refactor import restructure
from rope.refactor.importutils import ImportOrganizer

from core.core.logger import get_logger, log_execution
from core.core.utils import mask_sensitive_data, get_env_status
from .base_agent import BaseAgent

class RefactorAgent(BaseAgent):
    """
    Agente para refatoração automática de código Python usando Rope.
    
    Este agente analisa arquivos Python do repositório e aplica refatorações automaticamente,
    incluindo renomeação de variáveis, extração de métodos, organização de imports, etc.
    """
    
    # Níveis de refatoração disponíveis
    REFACTOR_LEVEL_LIGHT = "leve"
    REFACTOR_LEVEL_MODERATE = "moderado"
    REFACTOR_LEVEL_AGGRESSIVE = "agressivo"
    
    def __init__(self, project_dir: str, scope: Optional[str] = None, 
                 level: str = REFACTOR_LEVEL_MODERATE, dry_run: bool = False, 
                 force: bool = False, name: Optional[str] = None):
        """
        Inicializa o agente de refatoração.
        
        Args:
            project_dir: Diretório do projeto a ser refatorado
            scope: Escopo da refatoração (arquivo ou diretório específico)
            level: Nível de refatoração (leve, moderado, agressivo)
            dry_run: Se True, não aplica mudanças, apenas mostra o que seria feito
            force: Se True, ignora guardrails de segurança
            name: Nome do agente (opcional)
        """
        # Inicializa a classe base sem OpenAI/GitHub tokens
        super().__init__(name=name or "RefactorAgent", force=force)
        
        # Configuração específica do agente
        self.project_dir = os.path.abspath(project_dir)
        self.scope = scope
        self.level = level.lower() if level else self.REFACTOR_LEVEL_MODERATE
        self.dry_run = dry_run
        
        # Validar nível de refatoração
        valid_levels = [self.REFACTOR_LEVEL_LIGHT, self.REFACTOR_LEVEL_MODERATE, self.REFACTOR_LEVEL_AGGRESSIVE]
        if self.level not in valid_levels:
            self.logger.warning(f"Nível de refatoração inválido: {self.level}. Usando 'moderado'.")
            self.level = self.REFACTOR_LEVEL_MODERATE
            
        # Diretórios/arquivos a ignorar
        self.ignore_patterns = [
            r"^tests/",              # Diretório de testes
            r"^venv/",               # Ambiente virtual
            r"^\.venv/",             # Ambiente virtual alternativo
            r"^env/",                # Outro ambiente virtual
            r"^\.git/",              # Diretório git
            r"^__pycache__/",        # Cache Python
            r"^\.pytest_cache/",     # Cache de testes
            r"^build/",              # Diretório de build
            r"^dist/",               # Diretório de distribuição
            r".*\.pyc$",             # Arquivos compilados
            r".*\.pyo$",             # Arquivos otimizados
            r".*\.pyd$",             # Arquivos DLL
            r".*\.so$",              # Bibliotecas compartilhadas
            r".*\.egg-info/",        # Metadata de pacotes
            r".*\.egg/",             # Egg distributions
            r".*\.mypy_cache/",      # Cache mypy
        ]
        self.project = None
        
        # Métricas e estatísticas
        self.stats = {
            "files_analyzed": 0,
            "files_modified": 0,
            "refactorings_applied": 0,
            "errors": 0,
            "warnings": 0,
            "start_time": None,
            "end_time": None,
            "detailed_changes": [],
        }
        
        # Inicializar projeto Rope
        self._init_rope_project()
        
    def _init_rope_project(self):
        """Inicializa o projeto Rope."""
        try:
            self.logger.info(f"INÍCIO - Inicializando projeto Rope em: {self.project_dir}")
            self.project = rope.base.project.Project(self.project_dir)
            
            # Configurar padrões para ignorar
            self.project.prefs.set('python_files', '*.py')
            ignore_patterns = []
            for pattern in self.ignore_patterns:
                if pattern.startswith('^'):
                    # Remover ^ do início para compatibilidade com o Rope
                    pattern = pattern[1:]
                ignore_patterns.append(pattern)
            
            self.project.prefs.set('ignored_resources', ignore_patterns)
            self.logger.info(f"SUCESSO - Projeto Rope inicializado. Padrões ignorados: {ignore_patterns}")
        except Exception as e:
            self.logger.error(f"FALHA - Erro ao inicializar projeto Rope: {str(e)}", exc_info=True)
            raise
    
    def validate_required_tokens(self):
        """Sobrescreve a validação de tokens para que não seja necessário validar tokens."""
        # Não é necessário validar tokens para este agente
        pass
    
    def trace(self, message: str):
        """
        Registra mensagem de rastreamento para facilitar o debug.
        
        Args:
            message: Mensagem a ser registrada
        """
        self.logger.debug(f"TRACE - {message}")
        
    @log_execution
    def run(self) -> Dict[str, Any]:
        """
        Executa o processo de refatoração.
        
        Returns:
            Dict[str, Any]: Resultados da refatoração com estatísticas
        """
        self.stats["start_time"] = time.time()
        self.logger.info(f"INÍCIO - RefactorAgent.run | Modo: {'dry-run' if self.dry_run else 'aplicação'} | Nível: {self.level}")
        
        try:
            # Se escopo é um arquivo específico
            if self.scope and os.path.isfile(os.path.join(self.project_dir, self.scope)):
                self.trace(f"Escopo é um arquivo específico: {self.scope}")
                resource = self._get_resource(self.scope)
                if resource:
                    self._process_file(resource)
                else:
                    self.logger.warning(f"Arquivo não encontrado no projeto: {self.scope}")
                    self.stats["warnings"] += 1
            # Se escopo é um diretório específico
            elif self.scope and os.path.isdir(os.path.join(self.project_dir, self.scope)):
                self.trace(f"Escopo é um diretório: {self.scope}")
                self._process_directory(self.scope)
            # Escopo completo do projeto
            else:
                self.trace("Processando todo o projeto")
                self._process_directory("")
            
            # Organizar imports em todo o escopo, se nível moderado ou agressivo
            if self.level in [self.REFACTOR_LEVEL_MODERATE, self.REFACTOR_LEVEL_AGGRESSIVE]:
                self._organize_imports()
                
            # Salvar as mudanças se não for dry-run
            if not self.dry_run:
                self.trace("Salvando todas as mudanças")
                self.project.close()
            else:
                self.trace("Modo dry-run: nenhuma mudança será salva")
                
            self.stats["end_time"] = time.time()
            duration = self.stats["end_time"] - self.stats["start_time"]
            
            # Formatar resultado
            result = {
                "status": "success",
                "dry_run": self.dry_run,
                "level": self.level,
                "statistics": {
                    "files_analyzed": self.stats["files_analyzed"],
                    "files_modified": self.stats["files_modified"],
                    "refactorings_applied": self.stats["refactorings_applied"],
                    "errors": self.stats["errors"],
                    "warnings": self.stats["warnings"],
                    "duration_seconds": round(duration, 2)
                },
                "changes": self.stats["detailed_changes"]
            }
            
            self.logger.info(f"SUCESSO - RefactorAgent.run | Arquivos analisados: {self.stats['files_analyzed']} | Modificados: {self.stats['files_modified']} | Refatorações: {self.stats['refactorings_applied']} | Duração: {round(duration, 2)}s")
            return result
            
        except Exception as e:
            self.stats["end_time"] = time.time()
            duration = self.stats["end_time"] - self.stats["start_time"]
            
            self.logger.error(f"FALHA - RefactorAgent.run | Erro: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": str(e),
                "statistics": {
                    "files_analyzed": self.stats["files_analyzed"],
                    "files_modified": self.stats["files_modified"],
                    "refactorings_applied": self.stats["refactorings_applied"],
                    "errors": self.stats["errors"] + 1,
                    "warnings": self.stats["warnings"],
                    "duration_seconds": round(duration, 2)
                },
                "changes": self.stats["detailed_changes"]
            }
    
    def _should_ignore(self, path: str) -> bool:
        """
        Verifica se um caminho deve ser ignorado.
        
        Args:
            path: Caminho relativo ao projeto
            
        Returns:
            bool: True se o caminho deve ser ignorado
        """
        if not path.endswith('.py'):
            return True
            
        for pattern in self.ignore_patterns:
            if re.search(pattern, path):
                return True
                
        return False
    
    def _get_resource(self, path: str):
        """
        Obtém um recurso do projeto Rope.
        
        Args:
            path: Caminho relativo ao projeto
            
        Returns:
            rope.base.resources.Resource: Recurso do projeto
        """
        try:
            return libutils.path_to_resource(self.project, path)
        except exceptions.ResourceNotFoundError:
            self.logger.warning(f"Recurso não encontrado: {path}")
            return None
    
    def _process_directory(self, directory: str):
        """
        Processa todos os arquivos Python em um diretório.
        
        Args:
            directory: Diretório relativo ao projeto
        """
        full_path = os.path.join(self.project_dir, directory)
        self.trace(f"Processando diretório: {full_path}")
        
        for root, dirs, files in os.walk(full_path):
            # Filtrar diretórios a ignorar (para otimização)
            dirs[:] = [d for d in dirs if not self._should_ignore(os.path.join(root, d).replace(self.project_dir + os.path.sep, ''))]
            
            for file in files:
                if file.endswith('.py'):
                    # Criar caminho relativo para o Rope
                    rel_path = os.path.join(root, file).replace(self.project_dir + os.path.sep, '')
                    if not self._should_ignore(rel_path):
                        resource = self._get_resource(rel_path)
                        if resource:
                            self._process_file(resource)
    
    def _process_file(self, resource):
        """
        Processa um arquivo Python para refatoração.
        
        Args:
            resource: Recurso do projeto Rope
        """
        self.trace(f"Processando arquivo: {resource.path}")
        self.stats["files_analyzed"] += 1
        
        try:
            # Verificar se o arquivo foi modificado
            file_modified = False
            
            # Aplicar refatorações com base no nível
            if self.level == self.REFACTOR_LEVEL_LIGHT:
                # Nível leve: somente renomeação de variáveis com nomes muito curtos
                modified = self._rename_short_variables(resource)
                file_modified = file_modified or modified
                
            elif self.level == self.REFACTOR_LEVEL_MODERATE:
                # Nível moderado: renomeação + extração de variáveis para expressões complexas
                modified = self._rename_short_variables(resource)
                file_modified = file_modified or modified
                
                modified = self._extract_complex_expressions(resource)
                file_modified = file_modified or modified
                
            elif self.level == self.REFACTOR_LEVEL_AGGRESSIVE:
                # Nível agressivo: todas as refatorações disponíveis
                modified = self._rename_short_variables(resource)
                file_modified = file_modified or modified
                
                modified = self._extract_complex_expressions(resource)
                file_modified = file_modified or modified
                
                modified = self._extract_duplicated_code(resource)
                file_modified = file_modified or modified
            
            # Registrar se o arquivo foi modificado
            if file_modified:
                self.stats["files_modified"] += 1
                self.stats["detailed_changes"].append({
                    "file": resource.path,
                    "type": "multiple_refactorings"
                })
                
        except Exception as e:
            self.logger.error(f"Erro ao processar {resource.path}: {str(e)}", exc_info=True)
            self.stats["errors"] += 1
    
    def _rename_short_variables(self, resource) -> bool:
        """
        Renomeia variáveis com nomes muito curtos.
        
        Args:
            resource: Recurso do projeto Rope
            
        Returns:
            bool: True se alguma modificação foi feita
        """
        # TODO: Implementar análise de variáveis usando Rope
        # Por enquanto, apenas um stub sem implementação real
        self.trace(f"Verificando variáveis curtas em: {resource.path}")
        return False
    
    def _extract_complex_expressions(self, resource) -> bool:
        """
        Extrai expressões complexas para variáveis.
        
        Args:
            resource: Recurso do projeto Rope
            
        Returns:
            bool: True se alguma modificação foi feita
        """
        # TODO: Implementar identificação de expressões complexas
        self.trace(f"Verificando expressões complexas em: {resource.path}")
        return False
    
    def _extract_duplicated_code(self, resource) -> bool:
        """
        Extrai código duplicado para métodos.
        
        Args:
            resource: Recurso do projeto Rope
            
        Returns:
            bool: True se alguma modificação foi feita
        """
        # TODO: Implementar detecção de código duplicado
        self.trace(f"Verificando código duplicado em: {resource.path}")
        return False
    
    def _organize_imports(self):
        """Organiza imports em todos os arquivos do escopo."""
        self.trace("Organizando imports")
        try:
            # Se for um escopo específico, processar apenas este escopo
            if self.scope:
                if os.path.isfile(os.path.join(self.project_dir, self.scope)):
                    resource = self._get_resource(self.scope)
                    if resource:
                        self._organize_file_imports(resource)
                elif os.path.isdir(os.path.join(self.project_dir, self.scope)):
                    self._organize_directory_imports(self.scope)
            else:
                # Processar todo o projeto
                self._organize_directory_imports("")
                
        except Exception as e:
            self.logger.error(f"Erro ao organizar imports: {str(e)}", exc_info=True)
            self.stats["errors"] += 1
            
    def _organize_file_imports(self, resource):
        """
        Organiza imports em um arquivo específico.
        
        Args:
            resource: Recurso do projeto Rope
        """
        try:
            self.trace(f"Organizando imports em: {resource.path}")
            
            # Criar organizador de imports
            import_organizer = ImportOrganizer(self.project)
            
            # Organizar imports
            changes = import_organizer.organize_imports(resource)
            
            # Aplicar mudanças se não for dry-run
            if not self.dry_run and changes:
                changes.do()
                self.stats["refactorings_applied"] += 1
                self.stats["detailed_changes"].append({
                    "file": resource.path,
                    "type": "organize_imports"
                })
                
        except Exception as e:
            self.logger.error(f"Erro ao organizar imports em {resource.path}: {str(e)}", exc_info=True)
            self.stats["errors"] += 1
            
    def _organize_directory_imports(self, directory: str):
        """
        Organiza imports em todos os arquivos Python em um diretório.
        
        Args:
            directory: Diretório relativo ao projeto
        """
        full_path = os.path.join(self.project_dir, directory)
        self.trace(f"Organizando imports no diretório: {full_path}")
        
        for root, dirs, files in os.walk(full_path):
            # Filtrar diretórios a ignorar (para otimização)
            dirs[:] = [d for d in dirs if not self._should_ignore(os.path.join(root, d).replace(self.project_dir + os.path.sep, ''))]
            
            for file in files:
                if file.endswith('.py'):
                    # Criar caminho relativo para o Rope
                    rel_path = os.path.join(root, file).replace(self.project_dir + os.path.sep, '')
                    if not self._should_ignore(rel_path):
                        resource = self._get_resource(rel_path)
                        if resource:
                            self._organize_file_imports(resource)
    
    def get_diff(self) -> str:
        """
        Gera o diff das mudanças feitas.
        
        Returns:
            str: Diff no formato Git
        """
        # Rope não tem suporte nativo para diff
        # Esta é uma implementação simplificada que pode ser expandida
        return "Diff não disponível nesta versão" 
        
    def move_with_backup(self, source_path: str, target_path: str) -> bool:
        """
        Move um arquivo mantendo backup do original no diretório bak/.
        
        Args:
            source_path: Caminho de origem do arquivo
            target_path: Caminho de destino do arquivo
            
        Returns:
            bool: True se a operação foi bem-sucedida
        """
        try:
            self.trace(f"Movendo arquivo com backup: {source_path} → {target_path}")
            
            # Criar diretório bak/ se não existir
            bak_dir = os.path.join(self.project_dir, "bak")
            os.makedirs(bak_dir, exist_ok=True)
            
            # Criar caminho relativo para preservar a estrutura de diretórios
            rel_path = os.path.relpath(source_path, self.project_dir)
            backup_path = os.path.join(bak_dir, rel_path)
            
            # Criar diretórios para o backup se necessário
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Fazer backup do arquivo original
            if os.path.exists(source_path):
                shutil.copy2(source_path, backup_path)
                self.trace(f"Backup criado em: {backup_path}")
            
            # Criar diretórios para o destino se necessário
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            # Mover o arquivo
            if os.path.exists(source_path):
                shutil.move(source_path, target_path)
            
            # Verificar e remover diretórios vazios após a operação
            self.cleanup_empty_dirs(os.path.dirname(source_path))
            
            # Registrar operação nas estatísticas
            self.stats["refactorings_applied"] += 1
            self.stats["detailed_changes"].append({
                "type": "move_file",
                "source": rel_path,
                "target": os.path.relpath(target_path, self.project_dir),
                "backup": os.path.join("bak", rel_path)
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"FALHA - Erro ao mover arquivo com backup: {str(e)}", exc_info=True)
            self.stats["errors"] += 1
            return False
    
    def cleanup_empty_dirs(self, directory: str):
        """
        Remove recursivamente diretórios vazios.
        
        Args:
            directory: Diretório a verificar e potencialmente remover
        """
        try:
            if not os.path.exists(directory):
                return
                
            # Não remover a raiz do projeto
            if os.path.samefile(directory, self.project_dir):
                return
                
            # Ignorar diretório bak/
            if os.path.basename(directory) == "bak" and os.path.dirname(directory) == self.project_dir:
                return
                
            # Primeiro remover subdiretórios vazios
            for root, dirs, files in os.walk(directory, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    if os.path.exists(dir_path) and not os.listdir(dir_path):
                        self.trace(f"Removendo subdiretório vazio: {dir_path}")
                        os.rmdir(dir_path)
                        # Registrar nas estatísticas
                        self.stats["detailed_changes"].append({
                            "type": "remove_empty_dir",
                            "path": os.path.relpath(dir_path, self.project_dir)
                        })
                
            # Verificar se o diretório principal está vazio
            if not os.listdir(directory):
                self.trace(f"Removendo diretório vazio: {directory}")
                os.rmdir(directory)
                
                # Registrar nas estatísticas
                self.stats["detailed_changes"].append({
                    "type": "remove_empty_dir",
                    "path": os.path.relpath(directory, self.project_dir)
                })
                
                # Recursivamente verificar o diretório pai
                parent_dir = os.path.dirname(directory)
                self.cleanup_empty_dirs(parent_dir)
                
        except Exception as e:
            self.logger.warning(f"AVISO - Erro ao remover diretório vazio {directory}: {str(e)}")
            self.stats["warnings"] += 1
    
    def rename_file(self, old_path: str, new_path: str) -> bool:
        """
        Renomeia um arquivo com backup e limpeza automática.
        
        Args:
            old_path: Caminho original do arquivo
            new_path: Novo caminho do arquivo
            
        Returns:
            bool: True se a operação foi bem-sucedida
        """
        return self.move_with_backup(old_path, new_path) 