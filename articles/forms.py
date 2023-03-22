from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1',
                  'password2', 'profile_image']
