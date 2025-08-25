"""
Configuração de URLs da aplicação Connect Sync.
Define rotas para páginas públicas, autenticação e área do membro.
"""

from django.urls import path
from . import views

app_name = 'connect_sync'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('planos/', views.plans_view, name='plans'),
    path('plano/<int:plan_id>/cadastro/', views.signup_view, name='signup'),
    path('cadastro/sucesso/<int:subscription_id>/', views.subscription_success_view, name='subscription_success'),
    path('sobre/', views.about_view, name='about'),
    
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('dashboard/', views.member_dashboard, name='member_dashboard'),
    path('perfil/editar/', views.member_edit_personal_view, name='member_edit_personal'),
    path('assinatura/', views.member_subscription_manage_view, name='member_subscription_manage'),
    path('assinatura/trocar-plano/', views.member_change_plan_view, name='member_change_plan'),
    path('assinatura/cancelar/', views.member_cancel_subscription_view, name='member_cancel_subscription'),
    path('conta/excluir/', views.member_delete_account_view, name='member_delete_account'),
]
