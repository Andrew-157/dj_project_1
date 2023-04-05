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

personal = [
    path('personal/', views.personal_page, name='personal-page'),
    path('personal/publish/',
         views.PublishArticle.as_view(), name='publish-article'),
    path('personal/update/<int:article_id>/',
         views.update_article, name='update-article'),
    path('personal/delete/<int:article_id>/',
         views.delete_article, name='delete-article')
]

public = [
    path('public/articles/<int:article_id>/',
         views.public_article, name='public-article'),
    path('public/articles/<int:article_id>/like/',
         views.like_article, name='like-article'),
    path('public/articles/<int:article_id>/dislike/',
         views.dislike_article, name='dislike-article'),
    path('public/articles/<int:article_id>/comment/',
         views.comment_article, name='comment-article'),
    path('public/tags/<str:tag>/',
         views.find_articles_through_tag, name='tag-article'),
    path('public/authors/<str:author>/', views.author_page, name='author-page'),
    path('public/authors/<str:author>/subscribe/',
         views.subscribe_request, name='subscribe'),
    path('public/search/', views.search, name='search')
]

urlpatterns = urlpatterns\
    + user_manipulations\
    + personal\
    + public
