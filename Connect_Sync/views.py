"""
Views da aplicação Connect Sync para gerenciar autenticação de membros, 
exibição de planos, cadastros, dashboard pessoal e gerenciamento de assinaturas.
Implementa sistema de autenticação baseado em sessões.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from datetime import timedelta

from .models import Plan, Member, Subscription

def home_view(request):
    total_members = Member.objects.count()
    active_subscriptions = Subscription.objects.filter(status='active').count()
    available_plans = Plan.objects.filter(active=True).count()
    
    plans = Plan.objects.filter(active=True).order_by('order')[:3]
    
    context = {
        'plans': plans,
        'stats': {
            'total_members': total_members,
            'active_subscriptions': active_subscriptions,
            'available_plans': available_plans,
        }
    }
    
    return render(request, 'connect_sync/home.html', context)

def plans_view(request):
    plans = Plan.objects.filter(active=True).order_by('order')
    return render(request, 'connect_sync/plans.html', {'plans': plans})

def about_view(request):
    return render(request, 'connect_sync/about.html')

def signup_view(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        area_tecnologia = request.POST.get('area_tecnologia')
        empresa_atual = request.POST.get('empresa_atual', '')
        password = request.POST.get('password')
        
        if not full_name or not email or not area_tecnologia or not password:
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
            return render(request, 'connect_sync/signup.html', {'plan': plan})
        
        if Member.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está cadastrado.')
            return render(request, 'connect_sync/signup.html', {'plan': plan})
        
        try:
            member = Member.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                area_tecnologia=area_tecnologia,
                empresa_atual=empresa_atual
            )
            
            member.password_hash = password
            member.save()
            
            from datetime import timedelta
            from django.utils import timezone
            next_billing_date = timezone.now() + timedelta(days=30)
            
            subscription = Subscription.objects.create(
                member=member,
                plan=plan,
                status='active',
                next_billing=next_billing_date
            )
            
            messages.success(request, f'Parabéns! Você se cadastrou no plano {plan.name} com sucesso!')
            messages.info(request, f'📧 Enviamos as instruções de acesso para {email}')
            return redirect('connect_sync:subscription_success', subscription_id=subscription.id)
            
        except Exception as e:
            messages.error(request, 'Erro ao processar cadastro. Tente novamente.')
            return render(request, 'connect_sync/signup.html', {'plan': plan})
    
    return render(request, 'connect_sync/signup.html', {'plan': plan})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Por favor, preencha email e senha.')
            return render(request, 'connect_sync/login.html')
        
        try:
            member = Member.objects.get(email=email)
            
            if member.password_hash == password:
                request.session['member_id'] = member.id
                request.session['member_name'] = member.full_name
                
                messages.success(request, f'Bem-vindo de volta, {member.full_name}!')
                return redirect('connect_sync:member_dashboard')
            else:
                messages.error(request, 'Email ou senha incorretos.')
                
        except Member.DoesNotExist:
            messages.error(request, 'Email ou senha incorretos.')
    
    return render(request, 'connect_sync/login.html')

def logout_view(request):
    request.session.flush()
    messages.success(request, 'Você foi desconectado com sucesso!')
    return redirect('connect_sync:home')

def member_dashboard(request):
    member_id = request.session.get('member_id')
    if not member_id:
        messages.error(request, 'Você precisa estar logado para acessar esta página.')
        return redirect('connect_sync:login')
    
    member = get_object_or_404(Member, id=member_id)
    subscription = member.subscriptions.filter(status='active').first()
    
    context = {
        'member': member,
        'subscription': subscription,
    }
    return render(request, 'connect_sync/member_dashboard.html', context)

def member_edit_personal_view(request):
    member_id = request.session.get('member_id')
    if not member_id:
        messages.error(request, 'Você precisa estar logado para acessar esta página.')
        return redirect('connect_sync:login')
    
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        area_tecnologia = request.POST.get('area_tecnologia')
        empresa_atual = request.POST.get('empresa_atual', '')
        
        if not full_name or not email or not area_tecnologia:
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
            return render(request, 'connect_sync/member_edit_personal.html', {'member': member})
        
        if Member.objects.filter(email=email).exclude(id=member.id).exists():
            messages.error(request, 'Este email já está sendo usado por outro membro.')
            return render(request, 'connect_sync/member_edit_personal.html', {'member': member})
        
        try:
            member.full_name = full_name
            member.email = email
            member.phone = phone
            member.area_tecnologia = area_tecnologia
            member.empresa_atual = empresa_atual
            member.save()
            
            request.session['member_name'] = member.full_name
            
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('connect_sync:member_dashboard')
            
        except Exception as e:
            messages.error(request, 'Erro ao atualizar perfil. Tente novamente.')
    
    return render(request, 'connect_sync/member_edit_personal.html', {'member': member})

def member_subscription_manage_view(request):
    member_id = request.session.get('member_id')
    if not member_id:
        messages.error(request, 'Você precisa estar logado para acessar esta página.')
        return redirect('connect_sync:login')
    
    member = get_object_or_404(Member, id=member_id)
    subscription = member.subscriptions.filter(status='active').first()
    all_plans = Plan.objects.filter(active=True).order_by('order')
    
    context = {
        'member': member,
        'subscription': subscription,
        'all_plans': all_plans,
    }
    return render(request, 'connect_sync/member_subscription_manage.html', context)

@require_POST
def member_change_plan_view(request):
    member_id = request.session.get('member_id')
    if not member_id:
        messages.error(request, 'Você precisa estar logado para acessar esta página.')
        return redirect('connect_sync:login')
    
    member = get_object_or_404(Member, id=member_id)
    subscription = member.subscriptions.filter(status='active').first()
    
    if not subscription:
        messages.error(request, 'Nenhuma assinatura ativa encontrada.')
        return redirect('connect_sync:member_dashboard')
    
    new_plan_id = request.POST.get('new_plan_id')
    new_plan = get_object_or_404(Plan, id=new_plan_id)
    
    try:
        old_plan = subscription.plan.name
        subscription.plan = new_plan
        subscription.save()
        
        messages.success(request, f'Plano alterado de {old_plan} para {new_plan.name} com sucesso!')
        return redirect('connect_sync:member_subscription_manage')
        
    except Exception as e:
        messages.error(request, 'Erro ao alterar plano. Tente novamente.')
        return redirect('connect_sync:member_subscription_manage')

@require_POST
def member_cancel_subscription_view(request):
    member_id = request.session.get('member_id')
    if not member_id:
        messages.error(request, 'Você precisa estar logado para acessar esta página.')
        return redirect('connect_sync:login')
    
    member = get_object_or_404(Member, id=member_id)
    subscription = member.subscriptions.filter(status='active').first()
    
    if not subscription:
        messages.error(request, 'Nenhuma assinatura ativa encontrada.')
        return redirect('connect_sync:member_dashboard')
    
    try:
        subscription.cancel()
        messages.success(request, 'Assinatura cancelada com sucesso!')
        return redirect('connect_sync:member_dashboard')
        
    except Exception as e:
        messages.error(request, 'Erro ao cancelar assinatura. Tente novamente.')
        return redirect('connect_sync:member_subscription_manage')

@require_POST
@csrf_protect
def member_delete_account_view(request):
    member_id = request.session.get('member_id')
    if not member_id:
        messages.error(request, 'Você precisa estar logado para acessar esta página.')
        return redirect('connect_sync:login')
    
    member = get_object_or_404(Member, id=member_id)
    
    try:
        active_subscriptions = member.subscriptions.filter(status='active')
        for subscription in active_subscriptions:
            subscription.cancel()
        
        request.session.flush()
        
        member_name = member.full_name
        member.delete()
        
        messages.success(request, f'Conta de {member_name} excluída com sucesso!')
        return redirect('connect_sync:home')
        
    except Exception as e:
        messages.error(request, 'Erro ao excluir conta. Tente novamente.')
        return redirect('connect_sync:member_dashboard')

def subscription_success_view(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    return render(request, 'connect_sync/subscription_success.html', {'subscription': subscription})
