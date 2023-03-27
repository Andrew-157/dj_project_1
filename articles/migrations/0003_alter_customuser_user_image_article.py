# Generated by Django 4.1.7 on 2023-03-27 07:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0005_auto_20220424_2025'),
        ('articles', '0002_rename_profile_image_customuser_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_image',
            field=models.ImageField(upload_to='articles/images/users/'),
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('image', models.ImageField(upload_to='articles/images/articles/')),
                ('times_read', models.BigIntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
        ),
    ]