from django.contrib import admin
from django.utils.html import format_html
from .models import MediaContent, Post, Hashtag, Content


class BaseContentAdmin(admin.ModelAdmin):
    exclude = ["likes"]
    readonly_fields = ["likes_count", "created_at", "updated_at"]
    list_display = ("id", "owner", "likes_count", "created_at", "thumbnail_preview")
    list_filter = ("created_at", "owner")
    search_fields = ("description", "owner__username", "owner__email")
    ordering = ("-created_at",)

    def likes_count(self, obj):
        return obj.likes.count()

    likes_count.short_description = "Likes"

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover;" />',
                obj.thumbnail.url,
            )
        return "-"

    thumbnail_preview.short_description = "Thumbnail"


@admin.register(Post)
class PostAdmin(BaseContentAdmin):
    pass


@admin.register(MediaContent)
class MediaAdmin(BaseContentAdmin):
    list_display = BaseContentAdmin.list_display + ("media_type", "file_name")

    def file_name(self, obj):
        return obj.file.name.split("/")[-1] if obj.file else "-"

    file_name.short_description = "File"


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "content_count")
    search_fields = ("name",)
    ordering = ("name",)

    def content_count(self, obj):
        return obj.contents.count()

    content_count.short_description = "Used in"
