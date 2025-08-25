"""
Configuração da aplicação Connect Sync para Django.
"""

from django.apps import AppConfig


class ConnectSyncConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Connect_Sync'
