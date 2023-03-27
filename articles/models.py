from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    user_image = models.ImageField(upload_to='articles/images/')
