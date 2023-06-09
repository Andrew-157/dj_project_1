from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Article, Comment, SocialMedia


class CustomUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1',
                  'password2', 'user_image']


class ChangeCustomUserForm(UserChangeForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_image']


class PublishArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['author', 'pub_date', 'times_read']


class CommentArticleForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['content']


class SocialMediaForm(forms.ModelForm):

    class Meta:
        model = SocialMedia
        exclude = ['user']
