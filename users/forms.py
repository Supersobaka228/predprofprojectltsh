from django.core.exceptions import ValidationError
from django.db import models
from django import forms
from django.forms.widgets import PasswordInput
from pyexpat.errors import messages

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
                   "phone": TextInput(attrs={"class": "field__input"})
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
        user = User.objects.get(Q(email=username))
        try:
            # Ищем пользователя по username ИЛИ email
            user = User.objects.get(
                Q(username=username) | Q(email=username)
            )
        except User.DoesNotExist:
            # Также пробуем по email, если username содержит @
            if '@' in username:
                try:
                    user = User.objects.get(email=username)
                except User.DoesNotExist:
                    return None
            else:
                return None
        try:
            user = User.objects.get(password=password, email=username)
            p = User.objects.get(Q(email=username))
            return user
        except User.DoesNotExist:
            return None

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
