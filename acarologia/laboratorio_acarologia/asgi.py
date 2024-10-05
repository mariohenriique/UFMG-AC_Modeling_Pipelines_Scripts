"""
ASGI config for laboratorio_acarologia project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Define o módulo de configurações do Django para o projeto ASGI
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laboratorio_acarologia.settings')

# Obtém a aplicação ASGI padrão do Django
application = get_asgi_application()
