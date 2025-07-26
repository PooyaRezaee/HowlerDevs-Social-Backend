from rest_framework import serializers
from apps.comment.models import Comment
from django.utils.timesince import timesince
from datetime import datetime, timezone

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    count_replies = serializers.IntegerField(read_only=True)
    count_likes = serializers.IntegerField(read_only=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "user", "text", "reply", "count_replies", "count_likes", "created_at"]
        read_only_fields = ["id", "user", "count_replies", "count_likes", "created_at"]

    def get_user(self, obj):
        return obj.user.username if obj.user else None

    def get_created_at(self, obj):
        return timesince(obj.created_at, datetime.now(timezone.utc)) + " ago"

class CommentCreateSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=512)
    reply = serializers.IntegerField(required=False)