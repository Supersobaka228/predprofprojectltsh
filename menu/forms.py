from django.core.exceptions import ValidationError
from django.db import models
from django import forms
from django.forms.widgets import PasswordInput
from pyexpat.errors import messages

from menu.models import Review
from users.models import User


from django.forms import ModelForm, TextInput

class ReviewForm(ModelForm):
    error_messages = []
    review = models.TextField()
    class Meta:
        model = Review
        fields = ['review']
        widgets = {"review": TextInput(attrs={"class": "rate-textarea"})
                   }