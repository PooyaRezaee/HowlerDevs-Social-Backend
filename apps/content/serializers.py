import os
from rest_framework import serializers
from .models import Post, MediaContent, Content


class ContentOutputSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Content
        fields = ("id", "description", "user", "thumbnail")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(instance, Post) or hasattr(instance, "post"):
            data["content_type"] = "post"
        elif isinstance(instance, MediaContent) or hasattr(instance, "mediacontent"):
            data["content_type"] = "media"
        else:
            data["content_type"] = "unknown"
        data["count_likes"] = instance.likes.count()
        data["created_at"] = instance.created_at.timestamp()

        return data


class PostOutputSerializer(ContentOutputSerializer):
    class Meta:
        model = Post
        fields = ("id", "description", "user", "thumbnail")


class MediaContentOutputSerializer(ContentOutputSerializer):
    class Meta:
        model = MediaContent
        fields = (
            "id",
            "description",
            "user",
            "thumbnail",
            "media_type",
            "file",
        )


class ContentInputSerializer(serializers.ModelSerializer):
    pass


class PostInputSerializer(ContentInputSerializer):
    class Meta:
        model = Post
        fields = ("description", "thumbnail")


class MediaContentInputSerializer(ContentInputSerializer):
    """
    Create media content
    """
    class Meta:
        model = MediaContent
        fields = ("description", "thumbnail", "file", "media_type")

    def validate(self, attrs):
        file = attrs.get("file")
        media_type = attrs.get("media_type")

        if not file or not media_type:
            raise serializers.ValidationError("Both 'file' and 'media_type' are required.")

        valid_media_types = ["video", "audio"]
        if media_type not in valid_media_types:
            raise serializers.ValidationError({"media_type": "Invalid media_type. Must be 'video' or 'audio'."})

        ext = os.path.splitext(file.name)[1].lower()
        video_exts = [".mp4", ".mkv", ".avi", ".mov"]
        audio_exts = [".mp3", ".wav", ".aac", ".ogg"]

        if media_type == "video" and ext not in video_exts:
            raise serializers.ValidationError({"file": f"File extension {ext} is not valid for video."})
        if media_type == "audio" and ext not in audio_exts:
            raise serializers.ValidationError({"file": f"File extension {ext} is not valid for audio."})

        return attrs
    
class ContentUpdateInputSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=512)
