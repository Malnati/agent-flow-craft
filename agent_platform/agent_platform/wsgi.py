"""
WSGI config for agent_platform project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agent_platform.settings.production')

application = get_wsgi_application() 