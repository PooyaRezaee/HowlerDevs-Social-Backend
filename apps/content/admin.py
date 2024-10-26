from django.contrib import admin
from .models import Reel, Post


@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    exclude = ["likes"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    exclude = ["likes"]
