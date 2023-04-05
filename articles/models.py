from django.db import models
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager


class CustomUser(AbstractUser):
    user_image = models.ImageField(upload_to='articles/images/users/')


class SocialMedia(models.Model):
    FACEBOOK = 'Facebook'
    INSTAGRAM = 'Instagram'
    TIKTOK = 'TikTok'
    TWITTER = 'Twitter'
    YOUTUBE = 'Youtube'
    SOCIAL_MEDIA_TITLES = [
        (FACEBOOK, 'Facebook'),
        (INSTAGRAM, 'Instagram'),
        (TIKTOK, 'TikTok'),
        (TWITTER, 'Twitter'),
        (YOUTUBE, 'Youtube')
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    link = models.URLField(max_length=128, unique=True)
    social_media_title = models.CharField(
        max_length=16,
        choices=SOCIAL_MEDIA_TITLES
    )


class Article(models.Model):
    title = models.CharField(max_length=255, null=False)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='articles/images/articles/', null=False)
    times_read = models.BigIntegerField(default=0)
    tags = TaggableManager(help_text='Use comma to separate tags')
    pub_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        CustomUser, related_name='subscriber', on_delete=models.CASCADE)
    subscribe_to = models.ForeignKey(
        CustomUser, related_name='publisher', on_delete=models.CASCADE)


class Comment(models.Model):
    commentator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    content = models.TextField(null=False)
    is_author = models.BooleanField(default=False)
    pub_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.content


class Reaction(models.Model):
    value = models.SmallIntegerField()
    reaction_owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
