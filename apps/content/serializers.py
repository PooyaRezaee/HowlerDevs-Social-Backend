from rest_framework import serializers
from .models import Post, Reel


class ContentOutPutSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="owner.username")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["count_likes"] = instance.likes.count()
        data["created_at"] = instance.created_at.timestamp()

        return data


class PostOutPutSerializer(ContentOutPutSerializer):
    class Meta:
        model = Post
        fields = ("id", "description", "user", "thumbnail")


class ReelOutPutSerializer(ContentOutPutSerializer):
    class Meta:
        model = Reel
        fields = (
            "id",
            "description",
            "user",
            "thumbnail",
            "video",
            "sound",
        )


class ContentInputSerializer(serializers.ModelSerializer):
    pass


class PostInputSerializer(ContentInputSerializer):
    class Meta:
        model = Post
        fields = ("description", "thumbnail")


class ReelInputSerializer(ContentInputSerializer):
    """
    create reels
    """
    class Meta:
        model = Reel
        fields = ("description", "thumbnail", "video" ,"sound")

    
    def validate(self, attrs):
        video = attrs.get("video")
        sound = attrs.get("sound")

        if video and sound:
            raise serializers.ValidationError("Only one of video or sound can be provided.")

        if not video and not sound:
            raise serializers.ValidationError("Either video or sound must be provided.")

        return attrs


class ContentUpdateInputSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=512)
