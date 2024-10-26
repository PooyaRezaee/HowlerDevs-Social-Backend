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
        fields = ("id", "description", "thumbnail")


class ReelInputSerializer(ContentInputSerializer):
    class Meta:
        model = Reel
        fields = ("description",)


class ContentUpdateInputSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=512)
