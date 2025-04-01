#!/usr/bin/env python3
"""
Script de instalação do pacote.
"""
from setuptools import find_packages, setup

setup(
    name="agent-flow-craft",
    version="0.1.0",
    description="Framework para automação de fluxo de criação de features usando agentes de IA",
    author="Seu Nome",
    author_email="seu.email@exemplo.com",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "openrouter>=0.3.0",
        "deepseek>=0.2.0",
        "google-generativeai>=0.3.0",
        "rope>=1.10.0",
        "pygithub>=2.1.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
        "typer>=0.9.0",
        "pydantic>=2.0.0",
        "requests>=2.31.0",
        "tenacity>=8.2.0",
        "cachetools>=5.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agent-flow-craft=src.cli.cli:app",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
) 