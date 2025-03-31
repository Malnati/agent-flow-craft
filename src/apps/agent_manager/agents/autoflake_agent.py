"""
Agente para limpeza automática de código Python usando Autoflake.
Este agente remove imports não utilizados e variáveis não usadas.
"""
import os
import sys
import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Union

from core.core.logger import get_logger, log_execution
from core.core.utils import mask_sensitive_data, get_env_status
from .base_agent import BaseAgent

class AutoflakeAgent(BaseAgent):
    """
    Agente para limpeza automática de código Python usando Autoflake.
    
    Este agente analisa arquivos Python do repositório e remove automaticamente:
    - Imports não utilizados
    - Variáveis não usadas
    - Imports com estrela (*)
    
    Suporta diferentes níveis de agressividade e modo dry-run.
    """
    
    # Níveis de agressividade disponíveis
    AGGRESSIVENESS_LIGHT = 1    # Apenas limpa imports
    AGGRESSIVENESS_MODERATE = 2 # Limpa imports e variáveis
    AGGRESSIVENESS_AGGRESSIVE = 3 # Limpa imports, variáveis e expande imports com *
    
    def __init__(self, project_dir: str, scope: Optional[str] = None, 
                 aggressiveness: int = AGGRESSIVENESS_MODERATE, dry_run: bool = False, 
                 force: bool = False, name: Optional[str] = None):
        """
        Inicializa o agente de limpeza automática.
        
        Args:
            project_dir: Diretório do projeto a ser analisado
            scope: Escopo da limpeza (arquivo ou diretório específico)
            aggressiveness: Nível de agressividade (1 a 3)
            dry_run: Se True, não aplica mudanças, apenas mostra o que seria feito
            force: Se True, ignora guardrails de segurança
            name: Nome do agente (opcional)
        """
        # Inicializa a classe base sem OpenAI/GitHub tokens
        super().__init__(name=name or "AutoflakeAgent", force=force)
        
        # Configuração específica do agente
        self.project_dir = os.path.abspath(project_dir)
        self.scope = scope
        self.dry_run = dry_run
        
        # Validar nível de agressividade
        try:
            self.aggressiveness = int(aggressiveness)
            if self.aggressiveness < 1 or self.aggressiveness > 3:
                self.logger.warning(f"Nível de agressividade inválido: {self.aggressiveness}. Usando nível 2 (moderado).")
                self.aggressiveness = self.AGGRESSIVENESS_MODERATE
        except (ValueError, TypeError):
            self.logger.warning(f"Nível de agressividade inválido: {aggressiveness}. Usando nível 2 (moderado).")
            self.aggressiveness = self.AGGRESSIVENESS_MODERATE
            
        # Diretórios/arquivos a ignorar
        self.ignore_patterns = [
            "venv/",
            ".venv/",
            "__pycache__/",
            "dist/",
            "build/",
            "tests/",
            ".git/",
            ".pytest_cache/",
            ".mypy_cache/",
            "*.egg-info/",
            "*.egg/",
        ]
        
        # Métricas e estatísticas
        self.stats = {
            "files_analyzed": 0,
            "files_modified": 0,
            "lines_removed": 0,
            "errors": 0,
            "warnings": 0,
            "start_time": None,
            "end_time": None,
            "modified_files": [],
        }
        
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
        
    def _get_autoflake_options(self) -> List[str]:
        """
        Obtém as opções do autoflake com base no nível de agressividade.
        
        Returns:
            List[str]: Lista de opções para o comando autoflake
        """
        options = ["--recursive"]
        
        # Opções baseadas no nível de agressividade
        if self.aggressiveness >= self.AGGRESSIVENESS_LIGHT:
            options.append("--remove-all-unused-imports")
            
        if self.aggressiveness >= self.AGGRESSIVENESS_MODERATE:
            options.append("--remove-unused-variables")
            
        if self.aggressiveness >= self.AGGRESSIVENESS_AGGRESSIVE:
            options.append("--expand-star-imports")
            
        # Opções adicionais
        if not self.dry_run:
            options.append("--in-place")
            
        return options
    
    def _get_autoflake_command(self, target_path: str) -> List[str]:
        """
        Constrói o comando completo do autoflake.
        
        Args:
            target_path: Caminho do arquivo ou diretório a ser processado
            
        Returns:
            List[str]: Comando completo para execução
        """
        command = ["autoflake"]
        command.extend(self._get_autoflake_options())
        
        # Adicionar excludes
        for pattern in self.ignore_patterns:
            command.extend(["--exclude", pattern])
            
        # Adicionar alvo
        command.append(target_path)
        
        return command
    
    def _count_lines_in_file(self, filepath: str) -> int:
        """
        Conta o número de linhas em um arquivo.
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            int: Número de linhas
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except Exception as e:
            self.logger.error(f"Erro ao contar linhas no arquivo {filepath}: {str(e)}")
            return 0
            
    def _get_file_line_count_diff(self, before_counts: Dict[str, int], after_counts: Dict[str, int]) -> Dict[str, Dict[str, Any]]:
        """
        Calcula a diferença de número de linhas antes e depois da limpeza.
        
        Args:
            before_counts: Contagem de linhas antes da limpeza
            after_counts: Contagem de linhas depois da limpeza
            
        Returns:
            Dict[str, Dict[str, Any]]: Diferença de linhas por arquivo
        """
        result = {}
        total_removed = 0
        
        for filepath in before_counts:
            if filepath in after_counts:
                before = before_counts[filepath]
                after = after_counts[filepath]
                removed = before - after
                
                if removed > 0:
                    result[filepath] = {
                        "before": before,
                        "after": after,
                        "removed": removed
                    }
                    total_removed += removed
                    self.stats["files_modified"] += 1
                    self.stats["modified_files"].append(filepath)
        
        self.stats["lines_removed"] = total_removed
        return result
    
    def _run_autoflake(self, target_path: str) -> Dict[str, Any]:
        """
        Executa o autoflake em um arquivo ou diretório.
        
        Args:
            target_path: Caminho do arquivo ou diretório
            
        Returns:
            Dict[str, Any]: Resultados da execução
        """
        # Verificar se o caminho existe
        full_path = os.path.join(self.project_dir, target_path) if target_path else self.project_dir
        if not os.path.exists(full_path):
            self.logger.error(f"Caminho não encontrado: {full_path}")
            self.stats["errors"] += 1
            return {"status": "error", "message": f"Caminho não encontrado: {full_path}"}
            
        try:
            # Contagem de linhas antes da limpeza
            before_counts = {}
            
            # Se não for dry-run, contar linhas antes da limpeza
            if not self.dry_run:
                if os.path.isfile(full_path) and full_path.endswith('.py'):
                    before_counts[full_path] = self._count_lines_in_file(full_path)
                elif os.path.isdir(full_path):
                    for root, _, files in os.walk(full_path):
                        for file in files:
                            if file.endswith('.py'):
                                filepath = os.path.join(root, file)
                                # Verificar se o arquivo deve ser ignorado
                                if not any(pattern in filepath for pattern in self.ignore_patterns):
                                    before_counts[filepath] = self._count_lines_in_file(filepath)
            
            # Construir e executar o comando
            command = self._get_autoflake_command(full_path)
            self.logger.info(f"Executando comando: {' '.join(command)}")
            
            # Executar o comando
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False
            )
            
            # Processar saída
            output = result.stdout.strip()
            error = result.stderr.strip()
            
            if result.returncode != 0:
                self.logger.error(f"Erro ao executar autoflake: {error}")
                self.stats["errors"] += 1
                return {"status": "error", "message": error, "command": " ".join(command)}
                
            # Contagem de linhas depois da limpeza (se não for dry-run)
            after_counts = {}
            file_changes = {}
            
            if not self.dry_run and before_counts:
                if os.path.isfile(full_path):
                    after_counts[full_path] = self._count_lines_in_file(full_path)
                elif os.path.isdir(full_path):
                    for filepath in before_counts:
                        if os.path.exists(filepath):
                            after_counts[filepath] = self._count_lines_in_file(filepath)
                
                file_changes = self._get_file_line_count_diff(before_counts, after_counts)
            
            return {
                "status": "success",
                "command": " ".join(command),
                "output": output,
                "files_analyzed": len(before_counts),
                "files_modified": self.stats["files_modified"],
                "lines_removed": self.stats["lines_removed"],
                "file_changes": file_changes
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao executar autoflake: {str(e)}", exc_info=True)
            self.stats["errors"] += 1
            return {"status": "error", "message": str(e)}
    
    @log_execution
    def run(self) -> Dict[str, Any]:
        """
        Executa o processo de limpeza automática.
        
        Returns:
            Dict[str, Any]: Resultados da limpeza com estatísticas
        """
        self.stats["start_time"] = time.time()
        self.logger.info(f"INÍCIO - AutoflakeAgent.run | Modo: {'dry-run' if self.dry_run else 'aplicação'} | Agressividade: {self.aggressiveness}")
        
        try:
            # Verificar se o autoflake está instalado
            try:
                subprocess.run(["autoflake", "--version"], capture_output=True, check=True)
            except (subprocess.SubprocessError, FileNotFoundError):
                self.logger.error("Autoflake não encontrado. Instale com 'pip install autoflake'.")
                return {
                    "status": "error",
                    "message": "Autoflake não encontrado. Instale com 'pip install autoflake'.",
                    "statistics": self.stats
                }
                
            # Executar autoflake no escopo especificado
            target_path = self.scope if self.scope else ""
            result = self._run_autoflake(target_path)
            
            self.stats["end_time"] = time.time()
            duration = self.stats["end_time"] - self.stats["start_time"]
            
            # Atualizar estatísticas finais
            self.stats["files_analyzed"] = result.get("files_analyzed", 0)
            
            # Formatar resultado final
            final_result = {
                "status": result.get("status", "unknown"),
                "dry_run": self.dry_run,
                "aggressiveness": self.aggressiveness,
                "command": result.get("command", ""),
                "statistics": {
                    "files_analyzed": self.stats["files_analyzed"],
                    "files_modified": self.stats["files_modified"],
                    "lines_removed": self.stats["lines_removed"],
                    "errors": self.stats["errors"],
                    "warnings": self.stats["warnings"],
                    "duration_seconds": round(duration, 2)
                },
                "modified_files": self.stats["modified_files"],
                "file_changes": result.get("file_changes", {}),
                "message": result.get("message", "")
            }
            
            if result.get("status") == "success":
                self.logger.info(f"SUCESSO - AutoflakeAgent.run | Arquivos analisados: {self.stats['files_analyzed']} | Modificados: {self.stats['files_modified']} | Linhas removidas: {self.stats['lines_removed']} | Duração: {round(duration, 2)}s")
            else:
                self.logger.error(f"FALHA - AutoflakeAgent.run: {result.get('message', 'Erro desconhecido')}")
                
            return final_result
            
        except Exception as e:
            self.logger.error(f"FALHA - Erro ao executar AutoflakeAgent: {str(e)}", exc_info=True)
            
            self.stats["end_time"] = time.time()
            duration = self.stats["end_time"] - self.stats["start_time"]
            self.stats["errors"] += 1
            
            return {
                "status": "error",
                "dry_run": self.dry_run,
                "aggressiveness": self.aggressiveness,
                "message": str(e),
                "statistics": {
                    "files_analyzed": self.stats["files_analyzed"],
                    "files_modified": self.stats["files_modified"],
                    "lines_removed": self.stats["lines_removed"],
                    "errors": self.stats["errors"],
                    "warnings": self.stats["warnings"],
                    "duration_seconds": round(duration, 2)
                },
                "modified_files": self.stats["modified_files"],
                "file_changes": {}
            } 