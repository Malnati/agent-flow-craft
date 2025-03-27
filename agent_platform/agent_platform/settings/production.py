"""
Configurações de produção
"""
from .common import *
from .agents import *

DEBUG = False
ALLOWED_HOSTS = ['agentplatform.yourdomain.com']

# Configurações adicionais de segurança para produção
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_PRELOAD = True 