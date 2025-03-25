import coverage
import unittest
import os

def run_coverage():
    cov = coverage.Coverage()
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
