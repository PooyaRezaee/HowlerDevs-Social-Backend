from django.db import models
from django.core.exceptions import ValidationError
from apps.account.models import User


class Content(models.Model):  # multi-table inheritance
    thumbnail = models.ImageField(upload_to="content/img", blank=True, null=True)
    description = models.CharField(max_length=512)
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="contents",
        null=True,
        db_index=True,
    )
    likes = models.ManyToManyField(User, related_name="content_likes", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)


class Post(Content):
    pass


class MediaContent(Content):
    MEDIA_TYPE_CHOICES = (("video", "Video"), ("audio", "Audio"))

    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    file = models.FileField(upload_to="media/content")

    def clean(self):
        if not self.file:
            raise ValidationError("File is required.")
        if self.media_type not in dict(self.MEDIA_TYPE_CHOICES):
            raise ValidationError("Invalid media type.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Need for apply clean logic
        super().save(*args, **kwargs)


class Hashtag(models.Model):
    name = models.CharField(max_length=64, unique=True, db_index=True)
    contents = models.ManyToManyField("Content", related_name="hashtags", blank=True)

    def __str__(self):
        return self.name
