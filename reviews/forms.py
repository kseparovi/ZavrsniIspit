from django import forms
from .models import ProductReview
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Napiši svoju recenziju...'}),
        }
        labels = {
            'comment': 'Recenzija'
        }


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        help_texts = {
            'username': '',
            'password1': '',
            'password2': '',
        }
