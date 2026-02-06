from django.core.exceptions import ValidationError
from django.db import models
from django import forms
from django.forms.widgets import PasswordInput

from .models import User


from django.forms import ModelForm, TextInput

class RegisterForm(ModelForm):
    error_messages = []
    password2 = forms.CharField(
        label='Пароль',
        widget=PasswordInput(attrs={
            'class': 'field__input',
            'placeholder': 'Введите пароль'
        })
    )
    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'phone']
        widgets = {"email": TextInput(attrs={"class": "field__input"}),
                   "password": PasswordInput(attrs={"class": "field__input"}),
                   "password2": PasswordInput(attrs={"class": "field__input"}),
                   }

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Имя пользователя или Email',
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'field__label',
            'placeholder': 'Введите имя пользователя или email',
        })
    )

    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'field__label',
            'placeholder': 'Введите пароль'
        }),
        error_messages={'required': 'Это поле обязательно для заполнения'}
    )
    from django.contrib.auth import get_user_model
    model = get_user_model()
    fields = ['email', 'password']
    error_messages = []
    widgets = {"email": TextInput(attrs={"class": "field__input"}), "password": PasswordInput(attrs={"class": "field__input"})}

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def find_username(self):

        username = self.cleaned_data.get('username')
        from django.contrib.auth import get_user_model
        if not username:
            raise ValidationError('Поле не может быть пустым')
        try:
            from django.db.models import Q
            User = get_user_model()
            user = User.objects.get(models.Q(username=username) | models.Q(email=username))
        except get_user_model().DoesNotExist:
            raise ValidationError('Пользователя не существует')

        return username

    def clean_password(self):
        """
        Валидация пароля
        """

        password = self.cleaned_data.get('password')

        if not password:
            raise ValidationError('Поле не может быть пустым')

        if len(password) < 8:
            raise ValidationError('Пароль должен содержать минимум 8 символов')

        return password


    def authenticate(self, username, password):
        from django.db.models import Q
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None


    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        print(username, password)

        if username and password:
            # Попытка аутентификации
            from django.db.models import Q
            user = User.objects.get(Q(email=username))
            print(user.password)
            self.user_cache = self.authenticate(
                username,
                password
            )

            if self.user_cache is None:
                print(115)
                # Неправильные учетные данные
                return None
                raise ValidationError(
                    'Неверное имя пользователя или пароль',
                    code='invalid_login'
                )

            # Дополнительная проверка активности пользователя
            if not self.user_cache.is_active:
                return None
                raise ValidationError(
                    'Аккаунт неактивен',
                    code='inactive'
                )

        return cleaned_data

    def get_user(self):
        """
        Возвращает аутентифицированного пользователя
        """
        # print(self.request.POST.get('username'))
        # print(self.request.POST.get('password'))
        return self.user_cache

    def get_user_id(self):
        """
        Возвращает ID аутентифицированного пользователя
        """
        if self.user_cache:
            return self.user_cache.id
        return None




    def get_remember_me(self):
        return self.cleaned_data.get('remember_me')

    def set_error(self, a):
        self.error_messages.append(a)

class TopUpBalanceForm(forms.Form):
    amount = forms.CharField(
        label='Сумма пополнения (₽)',
        widget=forms.TextInput(attrs={
            'class': 'payment-input',
            'inputmode': 'decimal',
            'placeholder': 'Например: 150.00',
        })
    )

    def clean_amount(self):
        raw = (self.cleaned_data.get('amount') or '').strip()
        if not raw:
            raise ValidationError('Введите сумму')

        # поддерживаем запятую
        raw = raw.replace(',', '.')
        try:
            # работаем через Decimal-подобную проверку без float-ошибок: рубли + 2 знака
            parts = raw.split('.')
            if len(parts) > 2:
                raise ValueError
            rub = int(parts[0]) if parts[0] else 0
            kop = 0
            if len(parts) == 2:
                frac = parts[1]
                if len(frac) > 2:
                    # слишком много знаков
                    raise ValidationError('Слишком много знаков после запятой')
                kop = int((frac + '00')[:2]) if frac else 0
            amount_cents = rub * 100 + kop
        except ValidationError:
            raise
        except Exception:
            raise ValidationError('Некорректная сумма')

        if amount_cents <= 0:
            raise ValidationError('Сумма должна быть больше 0')

        return amount_cents
