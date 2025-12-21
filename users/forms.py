from django.forms.widgets import PasswordInput
from django import forms
from .models import User
from django.forms import ModelForm, TextInput

class RegisterForm(ModelForm):
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