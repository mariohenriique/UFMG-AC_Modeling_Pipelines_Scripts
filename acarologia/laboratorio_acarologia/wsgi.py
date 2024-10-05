"""
WSGI config for laboratorio_acarologia project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Define o módulo de configurações do Django para o projeto WSGI
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laboratorio_acarologia.settings')

# Obtém a aplicação WSGI padrão do Django
application = get_wsgi_application()
