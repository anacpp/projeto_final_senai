#!/usr/bin/env python
"""
Script para criar dados iniciais da plataforma Connect Sync
Execute após as migrações para popular o banco com planos e dados básicos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primeiroProjeto.settings')
django.setup()

from Connect_Sync.models import Plan

def create_initial_plans():
    """Cria os planos iniciais da plataforma"""
    
    print("🔄 Criando planos iniciais...")
    
    # Verificar se já existem planos
    if Plan.objects.exists():
        print("✅ Planos já existem no banco de dados!")
        for plan in Plan.objects.all():
            print(f"   - {plan.name}: R$ {plan.monthly_price}")
        return
    
    # Criar planos
    plans_data = [
        {
            'name': 'Connect Bronze',
            'description': 'Plano básico para iniciantes em tecnologia',
            'monthly_price': 29.90,
            'active': True,
            'order': 1
        },
        {
            'name': 'Connect Prata',
            'description': 'Plano intermediário com benefícios exclusivos',
            'monthly_price': 59.90,
            'active': True,
            'order': 2
        },
        {
            'name': 'Connect Ouro',
            'description': 'Plano premium com acesso completo',
            'monthly_price': 99.90,
            'active': True,
            'order': 3
        }
    ]
    
    created_plans = []
    for plan_data in plans_data:
        plan = Plan.objects.create(**plan_data)
        created_plans.append(plan)
        print(f"   ✅ Criado: {plan.name} - R$ {plan.monthly_price}")
    
    print(f"\n🎉 {len(created_plans)} planos criados com sucesso!")
    return created_plans

def main():
    """Função principal"""
    print("🚀 Inicializando dados da plataforma Connect Sync...")
    print("=" * 50)
    
    try:
        # Criar planos
        create_initial_plans()
        
        print("\n" + "=" * 50)
        print("✅ Dados iniciais criados com sucesso!")
        print("\n📝 Próximos passos:")
        print("   1. Execute: python manage.py runserver")
        print("   2. Acesse: http://localhost:8000")
        print("   3. Navegue para 'Planos' para ver os planos criados")
        print("\n🔗 URLs úteis:")
        print("   - Página inicial: http://localhost:8000")
        print("   - Planos: http://localhost:8000/planos/")
        print("   - Admin: http://localhost:8000/admin/")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados iniciais: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
