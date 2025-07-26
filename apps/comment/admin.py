from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "content", "short_text", "created_at", "reply_to", "likes_count")
    list_filter = ("created_at", "user")
    search_fields = ("text", "user__username", "content__description")
    readonly_fields = ("created_at", "likes_count")

    def short_text(self, obj):
        return (obj.text[:75] + "...") if len(obj.text) > 75 else obj.text
    short_text.short_description = "Comment Text"

    def reply_to(self, obj):
        return obj.reply.id if obj.reply else "-"
    reply_to.short_description = "Reply To (Comment ID)"

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = "Number of Likes"
