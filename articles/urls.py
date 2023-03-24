from django.urls import path
from django.views.generic import TemplateView
from . import views


app_name = 'articles'
urlpatterns = [
    path('', TemplateView.as_view(
        template_name='articles/index.html'), name='index'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('change_profile/', views.ChangeProfile.as_view(), name='change-profile'),
    path('password_reset/', views.password_reset_request, name='password-reset')
]
