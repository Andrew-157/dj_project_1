from django.contrib import admin
from .models import CustomUser, Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'pub_date', 'tag_list']

    def get_queryset(self, request):
        return super().get_queryset(request).\
            select_related('author').\
            prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']
