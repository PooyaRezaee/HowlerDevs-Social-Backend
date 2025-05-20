from django.db import models
from django.core.exceptions import ValidationError
from apps.account.models import User


class BaseContent(models.Model):
    thumbnail = models.ImageField(upload_to="content/img", blank=True, null=True)
    description = models.CharField(max_length=512)

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="%(class)s_contents",
        null=True,
        db_index=True,
    )
    likes = models.ManyToManyField(User, related_name="%(class)s_likes", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Post(BaseContent):
    pass


class Reel(BaseContent):
    video = models.FileField(upload_to="content/video", blank=True, null=True)
    sound = models.FileField(upload_to="content/sound", blank=True, null=True)

    def clean(self):  # add validation for sound and video
        if not self.video and not self.sound:
            raise ValidationError("Either video or sound must be provided.")
        if self.video and self.sound:
            raise ValidationError("Only one of video or sound can be provided.")

    def save(self, *args, **kwargs):
        # self.full_clean() # Need clean in logic
        super().save(*args, **kwargs)


class Hashtag(models.Model):
    name = models.CharField(max_length=64, unique=True, db_index=True)
    posts = models.ManyToManyField(Post, related_name="hashtags", blank=True)
    reels = models.ManyToManyField(Reel, related_name="hashtags", blank=True)

    def __str__(self):
        return self.name
