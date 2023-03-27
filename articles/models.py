from django.db import models
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager


class CustomUser(AbstractUser):
    user_image = models.ImageField(upload_to='articles/images/users/')


class Article(models.Model):
    title = models.CharField(max_length=255, null=False)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='articles/images/articles/')
    times_read = models.BigIntegerField(default=0)
    tags = TaggableManager()
