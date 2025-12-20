# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
import uuid


class User(AbstractUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('student', 'Ученик'),
        ('cook', 'Повар'),
        ('admin', 'Администратор'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(_('first name'), max_length=255)
    last_name = models.CharField(_('last name'), max_length=255)
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    phone = models.CharField(_('phone number'), max_length=11, unique=True)
    is_active = models.BooleanField(_('active'), default=True)
    role = models.CharField(_('role'), max_length=255, choices=ROLE_CHOICES)
    grade = models.CharField(_('grade'), max_length=3)
    balance = models.IntegerField(_('balance'), default=0)
    not_like = models.CharField(_('not like'), max_length=255)
    abonement = models.IntegerField(_('abonement'), default=0)
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        db_table = 'users'
        ordering = ('grade', 'last_name')

    def __str__(self):
        return self.email

