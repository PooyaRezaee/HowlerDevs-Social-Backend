from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from core.output_serializers import SuccessResponseSerializer, ErrorResponseSerializer
from apps.account.models import User
from .services.connection import (
    request_connection,
    reject_connection,
    accept_connection,
    remove_connection,
)
from .selectors.connection import (
    list_connection_user_received_request,
    list_connection_user_sent_request,
    list_connections,
    user_connected_to,
)


class ConnectToUserAPIView(APIView):
    """The connection request to the user is accepted immediately if the user is not private, otherwise it must wait for the user's confirmation"""

    permission_classes = [IsAuthenticated]

    class InputReqConnectionSerializer(serializers.Serializer):
        username = serializers.CharField(max_length=150)

    @extend_schema(
        summary="Request connection to user",
        request=InputReqConnectionSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorResponseSerializer,
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

    @extend_schema(
        summary="Accept connection request",
        request=InputAcpConnectionSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorResponseSerializer,
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

    @extend_schema(
        summary="Reject connection request",
        request=InputRejConnectionSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorResponseSerializer,
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


class ConnectionListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class ConnectionsInputSerializer(serializers.Serializer):
        username = serializers.CharField()

    class ConnectionsOutPutSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("username", "picture")

    @extend_schema(
        summary="List connections",
        request=ConnectionsInputSerializer,
        responses={
            200: ConnectionsOutPutSerializer,
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        input_srz = self.ConnectionsInputSerializer(data=request.data)
        input_srz.is_valid(raise_exception=True)

        try:
            user = User.objects.get(username=input_srz.data["username"])
            self_user = self.request.user
            if (
                user.is_private
                and not user_connected_to(user, self_user)
                and user != self_user
            ):
                return Response(
                    {"detail": "you must be connection this user to see"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            users = list_connections(user)
            srz = self.ConnectionsOutPutSerializer(users, many=True)
            # TODO need pagination
            return Response(srz.data)
        except ObjectDoesNotExist:
            return Response(
                {"detail": "username not found"}, status=status.HTTP_400_BAD_REQUEST
            )


class RequestConnectionListReceivedAPIView(APIView):
    """Return a list of incoming connection requests waiting for the authenticated user's approval."""

    permission_classes = [IsAuthenticated]

    class ReceivedConnectionsOutPutSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("username", "picture")

    @extend_schema(
        summary="List received connection requests",
        responses={
            200: ReceivedConnectionsOutPutSerializer,
            400: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        user = request.user
        connections = list_connection_user_received_request(user)
        srz = self.ReceivedConnectionsOutPutSerializer(
            [connection.requester for connection in connections], many=True
        )
        # TODO need pagination
        return Response(srz.data)


class RequestConnectionListSentAPIView(APIView):
    """Return a list pending connection rqeuests sent by the authenticated user."""

    permission_classes = [IsAuthenticated]

    class SentConnectionsOutPutSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("username", "picture")

    @extend_schema(
        summary="List sent connection requests",
        responses={
            200: SentConnectionsOutPutSerializer,
            400: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        user = request.user
        connections = list_connection_user_sent_request(user)
        srz = self.SentConnectionsOutPutSerializer(
            [connection.receiver for connection in connections], many=True
        )
        # TODO need pagination
        return Response(srz.data)


class ConnectionRemoveAPIView(APIView):
    """Remove an existing connection between you and another user."""
    permission_classes = [IsAuthenticated]

    class ConnectionRemoveOutputSerializer(serializers.Serializer):
        username = serializers.CharField()

    @extend_schema(
        summary="Remove connection",
        request=ConnectionRemoveOutputSerializer,
        responses={
            204: OpenApiResponse(description="Connection successfully removed."),
            400: OpenApiResponse(description="Connection does not exist."),
            404: OpenApiResponse(description="Target user not found."),
        }
    )
    def post(self, request):
        self.srz = self.ConnectionRemoveOutputSerializer(data=request.data)
        self.srz.is_valid(raise_exception=True)

        username = self.srz.validated_data["username"]
        requester = request.user
        receiver = get_object_or_404(User, username=username)

        if remove_connection(requester, receiver):
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"detail": "Connection does not exist."},
            status=status.HTTP_400_BAD_REQUEST,
        )
