from django.urls import path
from django.views.generic import TemplateView
from . import views


app_name = 'articles'
urlpatterns = [
    path('', TemplateView.as_view(
        template_name='articles/index.html'), name='index'),
    path('become_user/', TemplateView.
         as_view(template_name='articles/become_user.html'), name='become-user')
]

user_manipulations = [path('register/', views.RegisterUser.as_view(), name='register'),
                      path('login/', views.LoginUser.as_view(), name='login'),
                      path('logout/', views.logout_request, name='logout'),
                      path('change_user/', views.ChangeUser.as_view(),
                           name='change-user'),
                      path('password_reset/', views.password_reset_request, name='password-reset'),]

private = [path('publish_article/', views.PublishArticle.as_view(), name='publish-article'),
           path('update_article/<int:article_id>',
                views.update_article, name='update-article'),]

public = [
    path('public/<int:article_id>/', views.public_article, name='public-article'),
    path('public/<int:article_id>/like/',
         views.like_article, name='like-article'),
    path('public/<int:article_id>/dislike/',
         views.dislike_article, name='dislike-article')
]

urlpatterns = urlpatterns\
    + user_manipulations\
    + private\
    + public
