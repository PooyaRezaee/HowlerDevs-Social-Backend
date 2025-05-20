from rest_framework import serializers


class SuccessResponseSerializer(serializers.Serializer):
    status = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
