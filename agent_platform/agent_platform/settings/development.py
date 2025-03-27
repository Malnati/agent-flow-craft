"""
Configurações de desenvolvimento
"""
from .common import *
from .agents import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Configurações adicionais para desenvolvimento
INSTALLED_APPS += [
    'django_extensions',
] 