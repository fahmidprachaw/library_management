from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review


class RegistretionForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review']


class DepositeForm(forms.Form):
    amount = forms.DecimalField(label="Amount to Deposite", min_value=100)

