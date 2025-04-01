import os
import sys
import unittest
import coverage
from core.logger import get_logger, log_execution
from pathlib import Path

logger = get_logger(__name__)

# Configurar cache do pytest
os.environ.setdefault("PYTHONPYCACHEPREFIX", str(Path().absolute() / "out"))

@log_execution
def run_coverage():
    """
    Executa os testes com cobertura e gera relatórios.
    """
    logger.info("INÍCIO - run_coverage | Iniciando análise de cobertura")
    
    try:
        # Configurar o coverage
        cov = coverage.Coverage(
            source=['agents'],
            omit=['*/venv/*', '*/env/*', '*/tests/temp/*', '*/tests/fixtures/*'],
        )
        
        logger.debug("Coverage configurado | Source: agents")
        
        # Iniciar a cobertura
        cov.start()
        logger.info("Análise de cobertura iniciada")
        
        # Executar os testes
        tests = unittest.TestLoader().discover('.')
        result = unittest.TextTestRunner(verbosity=2).run(tests)
        
        logger.info(f"Execução dos testes concluída | Sucesso: {result.wasSuccessful()}")
        
        # Parar a cobertura
        cov.stop()
        
        # Gerar relatório
        logger.info("Gerando relatório de cobertura")
        coverage_percentage = cov.report()
        logger.info(f"SUCESSO - Cobertura total: {coverage_percentage:.2f}%")
        
        # Gerar relatório HTML
        cov.html_report(directory='coverage_html_report')
        logger.info("SUCESSO - Relatório HTML gerado em 'coverage_html_report'")
        
        return result.wasSuccessful()
        
    except Exception as e:
        logger.error(f"FALHA - run_coverage | Erro: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        success = run_coverage()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.critical(f"FALHA CRÍTICA - Erro na execução principal: {str(e)}", exc_info=True)
        sys.exit(1)
