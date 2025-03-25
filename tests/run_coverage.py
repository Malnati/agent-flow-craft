import unittest
import os
import sys
import coverage

def run_coverage():
    # Adicionar o diretório raiz ao PYTHONPATH
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)
    
    cov = coverage.Coverage(
        source=['agents', 'tests'],
        omit=['*/site-packages/*', 'tests/run_coverage.py']
    )
    cov.start()

    # Executa todos os testes
    tests = unittest.TestLoader().discover('./tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

    cov.stop()
    cov.save()
    print("\nRelatório de cobertura:")
    cov.report()

    # Gerar relatório HTML na pasta coverage_html_report
    cov.html_report(directory='coverage_html_report')
    print("\nRelatório HTML de cobertura gerado na pasta 'coverage_html_report'.")

if __name__ == '__main__':
    run_coverage()
