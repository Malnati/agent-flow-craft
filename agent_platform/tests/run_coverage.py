import os
import sys
import unittest
import coverage

# Adicionar diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_coverage():
    """
    Executa os testes com cobertura e gera relatórios.
    """
    # Configurar o coverage
    cov = coverage.Coverage(
        source=['agents'],
        omit=['*/venv/*', '*/env/*', '*/tests/temp/*', '*/tests/fixtures/*'],
    )
    
    # Iniciar a cobertura
    cov.start()
    
    # Executar os testes
    tests = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=2).run(tests)
    
    # Parar a cobertura
    cov.stop()
    
    # Gerar relatório
    print("\nRelatório de cobertura:")
    cov.report()
    
    # Gerar relatório HTML
    cov.html_report(directory='coverage_html_report')
    print("\nRelatório HTML de cobertura gerado na pasta 'coverage_html_report'.")

if __name__ == "__main__":
    run_coverage()
