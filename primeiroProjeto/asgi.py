"""
Configuração ASGI para o projeto Connect Sync.
Expõe a aplicação ASGI como variável para servidores assíncronos.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primeiroProjeto.settings')

application = get_asgi_application()
