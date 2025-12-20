from .models import User
from django.forms import ModelForm, TextInput

class RegisterForm(ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password', 'password2']
        widgets = {"email": TextInput(attrs={"class": "field__input"}),
                   "password": TextInput(attrs={"class": "field__input"}),
                   "password2": TextInput(attrs={"class": "field__input"})}