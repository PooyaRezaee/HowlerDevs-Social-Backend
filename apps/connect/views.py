from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiExample
from core import logger
from apps.account.models import User
from .services.connection import (
    request_connection,
    reject_connection,
    accept_connection,
)


class ConnectToUserAPIView(APIView):
    """The connection request to the user is accepted immediately if the user is not private, otherwise it must wait for the user's confirmation"""

    permission_classes = [IsAuthenticated]

    class InputReqConnectionSerializer(serializers.Serializer):
        username = serializers.CharField(max_length=150)

    class SuccessResponseReqConSerializer(serializers.Serializer):
        status = serializers.CharField(max_length=10)

    class ErrorResponseReqConSerializer(serializers.Serializer):
        detail = serializers.CharField(max_length=255)

    @extend_schema(
        request=InputReqConnectionSerializer,
        responses={
            200: SuccessResponseReqConSerializer,
            400: ErrorResponseReqConSerializer,
        },
        examples=[
            OpenApiExample(
                "Success - OK",
                value={"status": "ok"},
                response_only=True,
                description="When the connection request is immediately accepted.",
            ),
            OpenApiExample(
                "Success - Pending",
                value={"status": "pending"},
                response_only=True,
                description="When the connection request is waiting for the target user to accept.",
            ),
            OpenApiExample(
                "Error",
                value={"detail": "text error"},
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        requester = request.user
        srz = self.InputReqConnectionSerializer(data=request.data)
        srz.is_valid(raise_exception=True)
        try:
            target_user = User.objects.get(username=srz.data["username"])
            request_status, out = request_connection(
                requester=requester, receiver=target_user
            )
            if request_status:
                if out.is_accept:
                    return Response({"status": "ok"})
                else:
                    return Response({"status": "pending"})
            else:
                return Response({"detail": out}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(
                {"detail": "User does not exists."}, status=status.HTTP_400_BAD_REQUEST
            )


class AcceptConnectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class InputAcpConnectionSerializer(serializers.Serializer):
        username = serializers.CharField(max_length=150)

    class SuccessResponseAcpConSerializer(serializers.Serializer):
        status = serializers.CharField(max_length=10)

    class ErrorResponseAcpConSerializer(serializers.Serializer):
        detail = serializers.CharField(max_length=255)

    @extend_schema(
        request=InputAcpConnectionSerializer,
        responses={
            200: SuccessResponseAcpConSerializer,
            400: ErrorResponseAcpConSerializer,
        },
        examples=[
            OpenApiExample(
                "Success",
                value={"status": "ok"},
                response_only=True,
                description="When the connection request accepted",
            ),
            OpenApiExample(
                "Error",
                value={"detail": "text error"},
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        user = request.user
        srz = self.InputAcpConnectionSerializer(data=request.data)
        srz.is_valid(raise_exception=True)
        try:
            target_user = User.objects.get(username=srz.data["username"])
            status_accept = accept_connection(receiver=user, requester=target_user)
            if status_accept:
                return Response({"status": "ok"})
            else:
                return Response(
                    {"detail": "There is no request."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ObjectDoesNotExist:
            return Response(
                {"detail": "User does not exists."}, status=status.HTTP_400_BAD_REQUEST
            )


class RejectConnectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class InputRejConnectionSerializer(serializers.Serializer):
        username = serializers.CharField(max_length=150)

    class SuccessResponseRejConSerializer(serializers.Serializer):
        status = serializers.CharField(max_length=10)

    class ErrorResponseRejConSerializer(serializers.Serializer):
        detail = serializers.CharField(max_length=255)

    @extend_schema(
        request=InputRejConnectionSerializer,
        responses={
            200: SuccessResponseRejConSerializer,
            400: ErrorResponseRejConSerializer,
        },
        examples=[
            OpenApiExample(
                "Success",
                value={"status": "ok"},
                response_only=True,
                description="When the connection request rejected successfully",
            ),
            OpenApiExample(
                "Error",
                value={"detail": "text error"},
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        user = request.user
        srz = self.InputRejConnectionSerializer(data=request.data)
        srz.is_valid(raise_exception=True)
        try:
            target_user = User.objects.get(username=srz.data["username"])
            status_accept = reject_connection(receiver=user, requester=target_user)
            if status_accept:
                return Response({"status": "ok"})
            else:
                return Response(
                    {"detail": "There is no request."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ObjectDoesNotExist:
            return Response(
                {"detail": "User does not exists."}, status=status.HTTP_400_BAD_REQUEST
            )
