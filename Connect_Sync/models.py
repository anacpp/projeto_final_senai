from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import hashlib

# Create your models here.

class User(models.Model):
    """Modelo User customizado conforme solicitado pelo professor"""
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

class Member(models.Model):
    """Modelo baseado no diagrama - Membro do clube"""
    # Relacionamento com usuário customizado
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Campos principais do diagrama
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    password_hash = models.CharField(max_length=255, blank=True)
    
    # Dados profissionais
    area_tecnologia = models.CharField(max_length=50, blank=True)
    empresa_atual = models.CharField(max_length=200, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Member'
        verbose_name_plural = 'Members'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name

    def register(self):
        """Método do diagrama - registrar membro"""
        # Lógica de registro
        pass

    def login(self):
        """Método do diagrama - login do membro"""
        # Lógica de login
        pass


class Plan(models.Model):
    """Modelo baseado no diagrama - Planos de membership"""
    name = models.CharField(max_length=50, unique=True)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    
    # Campos extras para funcionalidades
    annual_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    color_theme = models.CharField(max_length=7, default='#007bff')
    active = models.BooleanField(default=True)
    order = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Plans'
        ordering = ['order', 'monthly_price']

    def __str__(self):
        return self.name

    def getBenefits(self):
        """Método do diagrama - obter benefícios do plano"""
        return self.benefits.filter(active=True)


class Subscription(models.Model):
    """Modelo baseado no diagrama - Assinatura do membro"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    started_at = models.DateTimeField(auto_now_add=True)
    next_billing = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Campos extras
    auto_renew = models.BooleanField(default=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.member.full_name} - {self.plan.name}"

    def renew(self):
        """Método do diagrama - renovar assinatura"""
        from datetime import timedelta
        if self.auto_renew and self.status == 'active':
            self.next_billing = timezone.now() + timedelta(days=30)
            self.save()

    def cancel(self):
        """Método do diagrama - cancelar assinatura"""
        self.status = 'cancelled'
        self.ended_at = timezone.now()
        self.save()


class Evento(models.Model):
    """Modelo baseado no diagrama (era Game) - Eventos tech"""
    title = models.CharField(max_length=200)
    event_date = models.DateTimeField()
    location = models.CharField(max_length=300)
    description = models.TextField()
    
    # Campos específicos para eventos tech
    speaker = models.CharField(max_length=200, blank=True)  # Era "opponent" no diagrama
    event_type = models.CharField(max_length=50, default='Tech Talk')
    max_attendees = models.IntegerField(null=True, blank=True)
    
    # Controle de acesso
    requires_membership = models.BooleanField(default=True)
    allowed_plans = models.ManyToManyField(Plan, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['event_date']

    def __str__(self):
        return f"{self.title} - {self.event_date.strftime('%d/%m/%Y')}"


class Ticket(models.Model):
    """Modelo baseado no diagrama - Ingressos para eventos"""
    owner = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='tickets')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='tickets')
    seat = models.CharField(max_length=20, blank=True)
    qr_code = models.CharField(max_length=100, unique=True)
    
    # Campos extras
    purchased_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        unique_together = ['owner', 'evento']
        ordering = ['-purchased_at']

    def __str__(self):
        return f"{self.owner.full_name} - {self.evento.title}"

    def purchase(self):
        """Método do diagrama - comprar ingresso"""
        # Gerar QR code único
        self.qr_code = hashlib.md5(f"{self.owner.id}-{self.evento.id}-{timezone.now()}".encode()).hexdigest()
        self.save()

    def validateQR(self):
        """Método do diagrama - validar QR code"""
        if not self.used:
            self.used = True
            self.used_at = timezone.now()
            self.save()
            return True
        return False


class Payment(models.Model):
    """Modelo baseado no diagrama - Pagamentos"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('pix', 'PIX'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Campos extras
    transaction_id = models.CharField(max_length=100, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.member.full_name} - R$ {self.amount} - {self.get_status_display()}"

    def process(self):
        """Método do diagrama - processar pagamento"""
        # Lógica de processamento do pagamento
        self.status = 'completed'
        self.processed_at = timezone.now()
        self.save()


class Benefit(models.Model):
    """Modelo baseado no diagrama - Benefícios/Códigos de desconto"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    provider = models.CharField(max_length=200)  # Empresa parceira
    
    # Campos específicos para códigos
    discount_code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.IntegerField()
    redeem_url = models.URLField()
    
    # Relacionamento com planos
    plans = models.ManyToManyField(Plan, related_name='benefits')
    
    # Controle de disponibilidade
    available_quantity = models.IntegerField(null=True, blank=True)
    used_quantity = models.IntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Benefit'
        verbose_name_plural = 'Benefits'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.discount_percentage}% OFF"

    def redeem(self, member):
        """Método do diagrama - resgatar benefício"""
        if self.can_redeem():
            # Criar registro de resgate
            BenefitRedemption.objects.create(
                member=member,
                benefit=self,
                redeemed_at=timezone.now()
            )
            self.used_quantity += 1
            self.save()
            return True
        return False

    def can_redeem(self):
        """Verifica se pode ser resgatado"""
        now = timezone.now()
        if not self.active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.available_quantity and self.used_quantity >= self.available_quantity:
            return False
        return True


class BenefitRedemption(models.Model):
    """Modelo para controlar resgates de benefícios"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    benefit = models.ForeignKey(Benefit, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    unique_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        verbose_name = 'Benefit Redemption'
        verbose_name_plural = 'Benefit Redemptions'
        unique_together = ['member', 'benefit']
        ordering = ['-redeemed_at']

    def __str__(self):
        return f"{self.member.full_name} - {self.benefit.title}"
