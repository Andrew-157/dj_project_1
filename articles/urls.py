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
    path('change_user/', views.ChangeUser.as_view(), name='change-user'),
    path('password_reset/', views.password_reset_request, name='password-reset'),
    path('publish_article/', views.PublishArticle.as_view(), name='publish-article'),
    path('update_article/<int:article_id>',
         views.update_article, name='update-article'),
    path('become_user/', TemplateView.
         as_view(template_name='articles/become_user.html'), name='become-user')
]
