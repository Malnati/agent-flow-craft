from setuptools import setup, find_packages

setup(
    name="agent_flow_craft",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "autogen",
        "pyyaml",
        "python-slugify",
        "openai",
        "asyncio"
    ],
    extras_require={
        'dev': [
            'wheel',
            'pytest',
            'build',
            'twine'
        ]
    },
    entry_points={
        'console_scripts': [
            'mcp_agent=src.core.apps.agent_manager.agents.feature_creation_agent:main',
        ],
    },
    python_requires='>=3.8',
) 