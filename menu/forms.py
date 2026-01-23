from django import forms
from .models import Review, Order


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'day', 'item', 'stars_count']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ваш отзыв...'
            }),
            'day': forms.TextInput(),
            'item': forms.NumberInput(),
            'stars_count': forms.NumberInput()

        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'time', 'price', 'day', 'user']
        widgets = {
            'name': forms.TextInput(),
            'time': forms.TextInput(),
            'price': forms.NumberInput(),
            'day': forms.TextInput(),
            'user_id': forms.IntegerField()
        }