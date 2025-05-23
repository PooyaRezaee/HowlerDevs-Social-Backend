from django.contrib import admin
from .models import MediaContent, Post


@admin.register(MediaContent)
class MediaAdmin(admin.ModelAdmin):
    exclude = ["likes"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    exclude = ["likes"]
