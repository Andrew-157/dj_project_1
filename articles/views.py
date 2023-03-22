from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.decorators import method_decorator
from .forms import NewUserForm
