# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')

        email = self.normalize_email(email)

        # Автоматически создаем username из email
        if 'username' not in extra_fields:
            username = email.split('@')[0]
            # Делаем username уникальным
            base_username = username
            counter = 1
            while self.model.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            extra_fields['username'] = username

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('role', 'admin_main')
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    username = models.CharField(max_length=150,
        unique=True,
        blank=True,
        null=True)
    ROLE_CHOICES = [
        ('student', 'Ученик'),
        ('cook', 'Повар'),
        ('admin_main', 'Администратор'),
    ]
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_auth = models.BooleanField(default=False)
    first_name = models.CharField(_('first name'), max_length=255, default='')
    last_name = models.CharField(_('last name'), max_length=255, default='')
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    phone = models.CharField(_('phone number'), max_length=11, blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True)
    role = models.CharField(_('role'), max_length=255, choices=ROLE_CHOICES, default='student')
    grade = models.CharField(_('grade'), max_length=3, default='')
    # Баланс храним в центах (минимальных единицах), чтобы избежать ошибок округления
    balance_cents = models.IntegerField(_('balance (cents)'), default=0)
    # Выбранные пользователем аллергены (фиксированный список из menu.Allergen)
    allergies = models.ManyToManyField('menu.Allergen', blank=True, related_name='users')
    not_like = models.CharField(_('not like'), max_length=255, default='')
    abonement = models.IntegerField(_('abonement'), default=0)
    subscription_expires_at = models.DateTimeField(_('subscription expires'), null=True, blank=True)

    @property
    def get_is_auth(self):
        if self.is_authenticated:
            return True
        else:
            return False

    def set_auth(self):
        self.is_auth = True
        self.save()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split('@')[0]
            base_username = self.username
            counter = 1
            while User.objects.filter(username=self.username).exists():
                self.username = f"{base_username}_{counter}"
                counter += 1
        super().save(*args, **kwargs)

    @property
    def balance_rub_str(self) -> str:
        """Баланс в рублях с 2 знаками после запятой (например, 123.45)."""
        cents = int(self.balance_cents or 0)
        rub = cents / 100
        return f"{rub:.2f}"

    @property
    def balance_rub(self) -> float:
        """Баланс в рублях (float) — только для отображения, не для расчётов."""
        return (int(self.balance_cents or 0)) / 100

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        db_table = 'users'
        ordering = ('grade', 'last_name')

    def __str__(self):
        return self.email


class BalanceTopUp(models.Model):
    """Журнал пополнений баланса.

    Важно: сам баланс в User меняем только на сервере в транзакции, а здесь фиксируем факт пополнения.
    """
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='balance_topups')
    amount_cents = models.PositiveIntegerField(_('amount (cents)'))
    created_at = models.DateTimeField(auto_now_add=True)
    # кто инициировал пополнение (например, админ), опционально
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_balance_topups',
    )
    comment = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Пополнение баланса"
        verbose_name_plural = "Пополнения баланса"

    def __str__(self):
        return f"{self.user} +{self.amount_cents}c ({self.created_at:%Y-%m-%d %H:%M})"
