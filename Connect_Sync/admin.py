"""
Configuração do painel administrativo Django para gerenciar todos os modelos da aplicação Connect Sync.
Define como os modelos são exibidos, filtrados e pesquisados no admin.
"""

from django.contrib import admin
from .models import User, Member, Plan, Subscription, Evento, Ticket, Payment, Benefit, BenefitRedemption

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined']
    ordering = ['-date_joined']

class MemberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'area_tecnologia', 'created_at']
    search_fields = ['full_name', 'email']
    list_filter = ['area_tecnologia', 'created_at']

class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'monthly_price', 'active', 'order']
    list_filter = ['active']
    ordering = ['order']

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['member', 'plan', 'status', 'started_at', 'next_billing']
    list_filter = ['status', 'plan']

class EventoAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_date', 'event_type', 'max_attendees']
    list_filter = ['event_type', 'requires_membership']

class TicketAdmin(admin.ModelAdmin):
    list_display = ['owner', 'evento', 'purchased_at', 'used']
    list_filter = ['used', 'purchased_at']

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['member', 'amount', 'method', 'status', 'created_at']
    list_filter = ['status', 'method']

class BenefitAdmin(admin.ModelAdmin):
    list_display = ['title', 'provider', 'discount_percentage', 'active']
    list_filter = ['active', 'provider']

class BenefitRedemptionAdmin(admin.ModelAdmin):
    list_display = ['member', 'benefit', 'redeemed_at', 'used']
    list_filter = ['used', 'redeemed_at']

admin.site.register(User, UserAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Evento, EventoAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Benefit, BenefitAdmin)
admin.site.register(BenefitRedemption, BenefitRedemptionAdmin)
