# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
import uuid
import random


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
        ('admin', 'Администратор'),
    ]
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_auth = models.BooleanField(default=False)
    first_name = models.CharField(_('first name'), max_length=255, default='')
    last_name = models.CharField(_('last name'), max_length=255, default='')
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    phone = models.CharField(_('phone number'), max_length=11, default='')
    is_active = models.BooleanField(_('active'), default=True)
    role = models.CharField(_('role'), max_length=255, choices=ROLE_CHOICES, default='student')
    grade = models.CharField(_('grade'), max_length=3, default='')
    balance = models.IntegerField(_('balance'), default=0)
    not_like = models.CharField(_('not like'), max_length=255, default='')
    abonement = models.IntegerField(_('abonement'), default=0)
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        db_table = 'users'
        ordering = ('grade', 'last_name')

    def __str__(self):
        return self.email

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





