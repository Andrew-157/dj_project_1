# Generated by Django 4.1.7 on 2023-03-27 08:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0003_alter_customuser_user_image_article'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Article',
        ),
    ]
