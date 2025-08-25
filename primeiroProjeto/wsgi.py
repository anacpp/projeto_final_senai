"""
Configuração WSGI para o projeto Connect Sync.
Expõe a aplicação WSGI como variável para servidores web.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primeiroProjeto.settings')

application = get_wsgi_application()
