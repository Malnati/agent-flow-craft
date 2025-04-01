"""
Configuração do sistema de logs.
"""
import logging
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

import os


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Configura um logger com suporte a console colorido e arquivo.

    Args:
        name: Nome do logger.
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Caminho para o arquivo de log.

    Returns:
        Logger configurado.
    """
    # Obtém configurações das variáveis de ambiente
    log_level = level or os.environ.get("LOG_LEVEL", "INFO")
    log_file = log_file or os.environ.get("LOG_FILE")

    # Cria o logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level.upper())

    # Remove handlers existentes
    logger.handlers = []

    # Configura o console handler com rich
    console = Console(color_system="auto")
    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=True,
        markup=True,
        rich_tracebacks=True,
    )
    console_handler.setLevel(log_level.upper())
    logger.addHandler(console_handler)

    # Configura o file handler se especificado
    if log_file:
        # Cria diretório se não existir
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Configura o file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level.upper())
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


# Logger global para uso em todo o projeto
logger = setup_logger("agent_flow_craft")


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado para um módulo específico.

    Args:
        name: Nome do módulo.

    Returns:
        Logger configurado.
    """
    return setup_logger(f"agent_flow_craft.{name}")


def log_error(error: Exception) -> None:
    """
    Registra um erro no log.

    Args:
        error: Exceção a ser registrada.
    """
    logger.error(f"Erro: {str(error)}", exc_info=True)


def log_warning(message: str) -> None:
    """
    Registra um aviso no log.

    Args:
        message: Mensagem de aviso.
    """
    logger.warning(message)


def log_info(message: str) -> None:
    """
    Registra uma informação no log.

    Args:
        message: Mensagem informativa.
    """
    logger.info(message)


def log_debug(message: str) -> None:
    """
    Registra uma mensagem de debug no log.

    Args:
        message: Mensagem de debug.
    """
    logger.debug(message) 