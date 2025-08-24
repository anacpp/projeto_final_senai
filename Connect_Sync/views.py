from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Plan, Member, Subscription

def home_view(request):
    """View para a página inicial com estatísticas dinâmicas"""
    # Estatísticas da plataforma
    total_members = Member.objects.count()
    active_subscriptions = Subscription.objects.filter(status='active').count()
    available_plans = Plan.objects.filter(active=True).count()
    
    # Planos para preview (máximo 3)
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
    """View para exibir todos os planos disponíveis"""
    plans = Plan.objects.filter(active=True).order_by('order')
    return render(request, 'connect_sync/plans.html', {'plans': plans})

def plan_detail_view(request, plan_id):
    """View para exibir detalhes de um plano específico"""
    plan = get_object_or_404(Plan, id=plan_id)
    return render(request, 'connect_sync/plan_detail.html', {'plan': plan})

def about_view(request):
    """View para página sobre"""
    return render(request, 'connect_sync/about.html')

def signup_view(request, plan_id):
    """View para cadastro de novo membro com plano selecionado"""
    plan = get_object_or_404(Plan, id=plan_id)
    
    if request.method == 'POST':
        # Processar dados do formulário
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        area_tecnologia = request.POST.get('area_tecnologia')
        empresa_atual = request.POST.get('empresa_atual', '')
        password = request.POST.get('password')
        
        # Validação básica
        if not full_name or not email or not area_tecnologia or not password:
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
            return render(request, 'connect_sync/signup.html', {'plan': plan})
        
        # Verificar se email já existe
        if Member.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está cadastrado.')
            return render(request, 'connect_sync/signup.html', {'plan': plan})
        
        try:
            # Criar novo membro
            member = Member.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                area_tecnologia=area_tecnologia,
                empresa_atual=empresa_atual
            )
            
            # Definir senha para o membro (você pode usar hash aqui)
            member.password_hash = password  # Em produção, use hash adequado
            member.save()
            
            # Calcular próxima data de cobrança (30 dias a partir de hoje)
            from datetime import timedelta
            from django.utils import timezone
            next_billing_date = timezone.now() + timedelta(days=30)
            
            # Criar assinatura
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
    """View para login do membro"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Por favor, preencha email e senha.')
            return render(request, 'connect_sync/login.html')
        
        try:
            # Buscar membro pelo email
            member = Member.objects.get(email=email)
            
            # Verificar senha (em produção, use hash adequado)
            if member.password_hash == password:
                # Criar sessão do membro
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
    """View para logout do membro"""
    request.session.flush()
    messages.success(request, 'Você foi desconectado com sucesso!')
    return redirect('connect_sync:home')

def member_dashboard(request):
    """Dashboard do membro logado"""
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
    """View para o membro editar seus próprios dados"""
    member_id = request.session.get('member_id')
    if not member_id:
        messages.error(request, 'Você precisa estar logado para acessar esta página.')
        return redirect('connect_sync:login')
    
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == 'POST':
        # Processar dados do formulário
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        area_tecnologia = request.POST.get('area_tecnologia')
        empresa_atual = request.POST.get('empresa_atual', '')
        
        # Validação básica
        if not full_name or not email or not area_tecnologia:
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
            return render(request, 'connect_sync/member_edit_personal.html', {'member': member})
        
        # Verificar se email já existe (exceto o próprio membro)
        if Member.objects.filter(email=email).exclude(id=member.id).exists():
            messages.error(request, 'Este email já está sendo usado por outro membro.')
            return render(request, 'connect_sync/member_edit_personal.html', {'member': member})
        
        try:
            # Atualizar dados do membro
            member.full_name = full_name
            member.email = email
            member.phone = phone
            member.area_tecnologia = area_tecnologia
            member.empresa_atual = empresa_atual
            member.save()
            
            # Atualizar nome na sessão
            request.session['member_name'] = member.full_name
            
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('connect_sync:member_dashboard')
            
        except Exception as e:
            messages.error(request, 'Erro ao atualizar perfil. Tente novamente.')
    
    return render(request, 'connect_sync/member_edit_personal.html', {'member': member})

def member_subscription_manage_view(request):
    """View para o membro gerenciar sua própria assinatura"""
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
    """View para o membro trocar seu próprio plano"""
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
    """View para o membro cancelar sua própria assinatura"""
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
def member_delete_account_view(request):
    """View para o membro excluir sua própria conta"""
    member_id = request.session.get('member_id')
    if not member_id:
        messages.error(request, 'Você precisa estar logado para acessar esta página.')
        return redirect('connect_sync:login')
    
    member = get_object_or_404(Member, id=member_id)
    
    try:
        # Cancelar todas as assinaturas ativas primeiro
        active_subscriptions = member.subscriptions.filter(status='active')
        for subscription in active_subscriptions:
            subscription.cancel()
        
        # Limpar sessão
        request.session.flush()
        
        # Excluir o membro
        member_name = member.full_name
        member.delete()
        
        messages.success(request, f'Conta de {member_name} excluída com sucesso!')
        return redirect('connect_sync:home')
        
    except Exception as e:
        messages.error(request, 'Erro ao excluir conta. Tente novamente.')
        return redirect('connect_sync:member_dashboard')

def subscription_success_view(request, subscription_id):
    """View para página de sucesso após cadastro"""
    subscription = get_object_or_404(Subscription, id=subscription_id)
    return render(request, 'connect_sync/subscription_success.html', {'subscription': subscription})

# ====== CRUD VIEWS ======

def member_profile_view(request, member_id):
    """View para exibir perfil do membro"""
    member = get_object_or_404(Member, id=member_id)
    subscription = member.subscriptions.filter(status='active').first()
    
    context = {
        'member': member,
        'subscription': subscription,
    }
    return render(request, 'connect_sync/member_profile.html', context)

def member_edit_view(request, member_id):
    """View para editar dados do membro (UPDATE)"""
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == 'POST':
        # Processar dados do formulário
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        area_tecnologia = request.POST.get('area_tecnologia')
        empresa_atual = request.POST.get('empresa_atual', '')
        
        # Validação básica
        if not full_name or not email or not area_tecnologia:
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
            return render(request, 'connect_sync/member_edit.html', {'member': member})
        
        # Verificar se email já existe (exceto o próprio membro)
        if Member.objects.filter(email=email).exclude(id=member.id).exists():
            messages.error(request, 'Este email já está sendo usado por outro membro.')
            return render(request, 'connect_sync/member_edit.html', {'member': member})
        
        try:
            # Atualizar dados do membro (UPDATE)
            member.full_name = full_name
            member.email = email
            member.phone = phone
            member.area_tecnologia = area_tecnologia
            member.empresa_atual = empresa_atual
            member.save()
            
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('connect_sync:member_profile', member_id=member.id)
            
        except Exception as e:
            messages.error(request, 'Erro ao atualizar perfil. Tente novamente.')
            return render(request, 'connect_sync/member_edit.html', {'member': member})
    
    return render(request, 'connect_sync/member_edit.html', {'member': member})

def subscription_manage_view(request, member_id):
    """View para gerenciar assinatura do membro"""
    member = get_object_or_404(Member, id=member_id)
    subscription = member.subscriptions.filter(status='active').first()
    all_plans = Plan.objects.filter(active=True).order_by('order')
    
    context = {
        'member': member,
        'subscription': subscription,
        'all_plans': all_plans,
    }
    return render(request, 'connect_sync/subscription_manage.html', context)

@require_POST
def subscription_change_plan_view(request, member_id):
    """View para trocar plano da assinatura (UPDATE)"""
    member = get_object_or_404(Member, id=member_id)
    subscription = member.subscriptions.filter(status='active').first()
    
    if not subscription:
        messages.error(request, 'Nenhuma assinatura ativa encontrada.')
        return redirect('connect_sync:member_profile', member_id=member.id)
    
    new_plan_id = request.POST.get('new_plan_id')
    new_plan = get_object_or_404(Plan, id=new_plan_id)
    
    try:
        # Atualizar plano da assinatura (UPDATE)
        old_plan = subscription.plan.name
        subscription.plan = new_plan
        subscription.save()
        
        messages.success(request, f'Plano alterado de {old_plan} para {new_plan.name} com sucesso!')
        return redirect('connect_sync:subscription_manage', member_id=member.id)
        
    except Exception as e:
        messages.error(request, 'Erro ao alterar plano. Tente novamente.')
        return redirect('connect_sync:subscription_manage', member_id=member.id)

@require_POST
def subscription_cancel_view(request, member_id):
    """View para cancelar assinatura (UPDATE - soft delete)"""
    member = get_object_or_404(Member, id=member_id)
    subscription = member.subscriptions.filter(status='active').first()
    
    if not subscription:
        messages.error(request, 'Nenhuma assinatura ativa encontrada.')
        return redirect('connect_sync:member_profile', member_id=member.id)
    
    try:
        # Cancelar assinatura (UPDATE - soft delete)
        subscription.cancel()  # Método definido no modelo
        
        messages.success(request, 'Assinatura cancelada com sucesso!')
        return redirect('connect_sync:member_profile', member_id=member.id)
        
    except Exception as e:
        messages.error(request, 'Erro ao cancelar assinatura. Tente novamente.')
        return redirect('connect_sync:subscription_manage', member_id=member.id)

@require_POST
def member_delete_view(request, member_id):
    """View para excluir conta do membro (DELETE)"""
    member = get_object_or_404(Member, id=member_id)
    
    try:
        # Cancelar todas as assinaturas ativas primeiro
        active_subscriptions = member.subscriptions.filter(status='active')
        for subscription in active_subscriptions:
            subscription.cancel()
        
        # Excluir o membro (DELETE)
        member_name = member.full_name
        member.delete()
        
        messages.success(request, f'Conta de {member_name} excluída com sucesso!')
        return redirect('connect_sync:home')
        
    except Exception as e:
        messages.error(request, 'Erro ao excluir conta. Tente novamente.')
        return redirect('connect_sync:member_profile', member_id=member.id)

def members_list_view(request):
    """View para listar todos os membros (READ)"""
    members = Member.objects.all().order_by('-created_at')
    
    context = {
        'members': members,
    }
    return render(request, 'connect_sync/members_list.html', context)
