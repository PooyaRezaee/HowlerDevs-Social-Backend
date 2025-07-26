from django.db import models
from apps.content.models import Content, User


class Comment(models.Model):
    content = models.ForeignKey(Content, models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, models.CASCADE, related_name="comments")
    reply = models.ForeignKey(
        "self", models.CASCADE, related_name="replies", blank=True, null=True
    )
    likes = models.ManyToManyField(User, related_name="comment_likes", blank=True)
    text = models.CharField(max_length=512)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.content} | {self.user}"

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"
        indexes = [
            models.Index(fields=["content"]),
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
        ]