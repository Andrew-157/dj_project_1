from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.views import View
from .forms import CustomUserForm, ChangeCustomUserForm


class RegisterUser(View):
    form_class = CustomUserForm

    template_name = 'articles/register.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            username = form.cleaned_data['username']
            messages.success(request, f'Welcome to the Articlee, {username}')
            return redirect('articles:index')

        return render(request, self.template_name, {'form': form})


class LoginUser(View):
    form_class = AuthenticationForm
    template_name = 'articles/login.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(
                    request, f"Welcome back to the Articlee, {username}")
                return redirect('articles:index')
        return render(request, self.template_name, {'form': form})


def logout_request(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('articles:index')


class ChangeProfile(View):
    form_class = ChangeCustomUserForm
    template_name = 'articles/change_profile.html'

    def get(self, request):
        current_user = request.user
        form = self.form_class(instance=current_user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        current_user = request.user
        form = self.form_class(
            request.POST, request.FILES, instance=current_user)
        if form.is_valid():
            user = form.save()
            login(request, user)
            username = form.cleaned_data['username']
            messages.success(request, f'Welcome to the Articlee, {username}')
            return redirect('articles:index')

        return render(request, self.template_name, {'form': form})
