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
    path('personal/articles/publish/',
         views.PublishArticle.as_view(), name='publish-article'),
    path('personal/articles/<int:article_id>/update/',
         views.update_article, name='update-article'),
    path('personal/articles/<int:article_id>/delete/',
         views.delete_article, name='delete-article'),
    path('personal/social_media/add/',
         views.AddSocialMediaLink.as_view(), name='add-social-media'),
    path('personal/social_media/<int:social_media_id>/delete/',
         views.delete_social_media, name='delete-social-media'),
    path('personal/reading_history/',
         views.reading_history, name='reading-history'),
    path('personal/reading_history/clear/',
         views.clear_reading_history, name='clear-history'),
    path('personal/reading_history/<int:article_id>/delete/',
         views.delete_reading, name='delete-reading'),
    path('personal/articles/liked/', views.liked_articles, name='liked-articles'),
    path('personal/articles/disliked/',
         views.disliked_articles, name='disliked-articles'),
    path('personal/subscriptions/', views.subscriptions, name='subscriptions'),
    path('personal/articles/favorites', views.favorite_articles, name='favorites'),
    path('personal/articles/favorites/<int:article_id>/',
         views.favorites_request, name='favorites-manage')
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
    path('public/search/', views.search_articles, name='search-articles'),
]

urlpatterns = urlpatterns\
    + user_manipulations\
    + personal\
    + public
