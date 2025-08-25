"""
Configuração principal de URLs do projeto Connect Sync.
Redireciona URLs para aplicações específicas.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Connect_Sync.urls')),
]
