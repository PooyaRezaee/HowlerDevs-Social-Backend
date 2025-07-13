import uuid
import pyotp
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.cache import cache
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers, status
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    PolymorphicProxySerializer,
    OpenApiParameter,
)
from rest_framework_simplejwt.tokens import RefreshToken

from apps.connect.selectors.connection import count_connections
from apps.content.selectors.content import get_content_by_owner
from apps.connect.selectors.connection import user_connected_to
from core import logger
from .models import User
from .services.user import create_user
from .validators import validate_password
from .services.password import (
    send_password_reset_code,
    reset_user_password_with_code,
    change_user_password,
)
from .services.email import send_email_change_request, confirm_email_change
from .services.totp import setup_totp_for_user, verify_totp_code
from .enums import CacheKeyPrefix


class RegisterAPIView(APIView):
    """
    Handles new user registration.
    """

    authentication_classes = []

    class InputRegisterSerializer(serializers.Serializer):
        username = serializers.CharField(max_length=150)
        password = serializers.CharField(validators=[validate_password])

    class OutputRegisterSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("username", "joined_at")

    @extend_schema(
        summary="Register a new user",
        description="Creates a new user account with a username and password.",
        request=InputRegisterSerializer,
        responses={
            200: OutputRegisterSerializer,
            400: OpenApiResponse(description="Invalid input data."),
            500: OpenApiResponse(description="Internal server error."),
        },
        tags=["Auth"],
    )
    def post(self, request):
        srz = self.InputRegisterSerializer(data=request.data)
        srz.is_valid(raise_exception=True)

        try:
            username = srz.validated_data["username"]
            password = srz.validated_data["password"]
            user = create_user(username, password)
            return Response(
                self.OutputRegisterSerializer(user).data, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error in register user {e}")
            return Response(
                {"detail": "Internal Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProfileUpdateAPIView(APIView):
    """
    Updates the profile information for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    class InputProfileUpdateSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("full_name", "bio", "is_private", "email")

    class OutputProfileUpdateSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("username", "full_name", "bio", "is_private", "email")

    @extend_schema(
        summary="Update user profile",
        description="Allows an authenticated user to update their full name, bio, privacy status, and email. Email can only be set once.",
        request=InputProfileUpdateSerializer,
        responses={
            200: OutputProfileUpdateSerializer,
            400: OpenApiResponse(
                description="Bad request, e.g., trying to change email when it's already set."
            ),
        },
        tags=["Profile"],
    )
    def patch(self, request):
        user = request.user
        data = request.data.copy()

        if "email" in data:
            if user.email:
                return Response(
                    {"detail": "You can only set your email once."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        srz = self.InputProfileUpdateSerializer(user, data=request.data, partial=True)
        srz.is_valid(raise_exception=True)

        try:
            srz.save()
            return Response(self.OutputProfileUpdateSerializer(user).data)
        except Exception as e:
            logger.error(f"Error updating profile info for {user.username}: {e}")
            return Response(
                {"detail": "Internal Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProfileAvatarUpdateAPIView(APIView):
    """
    Updates the avatar for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    class ProfileAvatarUpdateSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("picture",)

    @extend_schema(
        summary="Update user avatar",
        description="Allows an authenticated user to upload or change their profile picture.",
        request=ProfileAvatarUpdateSerializer,
        responses={200: ProfileAvatarUpdateSerializer},
        tags=["Profile"],
    )
    def patch(self, request):
        user = request.user
        srz = self.ProfileAvatarUpdateSerializer(user, data=request.data, partial=True)
        srz.is_valid(raise_exception=True)

        try:
            srz.save()
            return Response(srz.data)
        except Exception as e:
            logger.error(f"Error updating profile picture for {user.username}: {e}")
            return Response(
                {"detail": "Internal Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProfileRetrieveAPIView(APIView):
    """
    Retrieves a user's profile.
    Shows public data to all users, but includes email for the profile owner.
    """

    class OutputProfileSerializer(serializers.ModelSerializer):
        connections_count = serializers.IntegerField()

        posts_count = serializers.IntegerField()

        class Meta:
            model = User
            fields = (
                "username",
                "full_name",
                "bio",
                "picture",
                "is_private",
                "connections_count",
                "posts_count",
            )

    class OutputSelfProfileSerializer(OutputProfileSerializer):
        class Meta:
            model = User
            fields = (
                "username",
                "full_name",
                "bio",
                "picture",
                "is_private",
                "connections_count",
                "posts_count",
                "email",
            )

    @extend_schema(
        summary="Retrieve a user profile",
        description="Fetches a user's profile by username. If the requester is the profile owner, the email is also returned. Access to private profiles is restricted.",
        parameters=[
            OpenApiParameter(
                name="username",
                description="The username of the profile to retrieve.",
                required=True,
                type=str,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={
            200: PolymorphicProxySerializer(
                component_name="UserProfile",
                serializers=[OutputSelfProfileSerializer, OutputProfileSerializer],
                resource_type_field_name=None,
            ),
            403: OpenApiResponse(
                description="The requested profile is private and you are not connected."
            ),
            404: OpenApiResponse(description="User not found."),
        },
        tags=["Profile"],
    )
    def get(self, request, username: str):
        # If the user is viewing their own profile
        if request.user.is_authenticated and request.user.username == username:
            user_obj = request.user
            srz_data = self.OutputSelfProfileSerializer(
                user_obj, context={"request": request}
            ).data
        else:
            user_obj = get_object_or_404(User, username=username)
            # Check for privacy settings
            if user_obj.is_private:
                if not request.user.is_authenticated or not user_connected_to(
                    request.user, user_obj
                ):
                    return Response(
                        {"detail": "This profile is private."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            srz_data = self.OutputProfileSerializer(
                user_obj, context={"request": request}
            ).data

        # Add aggregated counts
        srz_data["connections_count"] = count_connections(user_obj)
        srz_data["posts_count"] = get_content_by_owner(user_obj.username).count()

        return Response(srz_data)


class LoginView(APIView):
    """
    Handles user login.
    """
    class LoginSerializer(serializers.Serializer):
        username = serializers.CharField()
        password = serializers.CharField(write_only=True)

        def validate(self, attrs):
            user = authenticate(
                username=attrs["username"],
                password=attrs["password"],
            )
            if not user:
                raise serializers.ValidationError("Username or password is wrong!")

            if not user.is_2fa_enabled:
                refresh = RefreshToken.for_user(user)
                return {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "2fa_required": False,
                }

            temp_token = uuid.uuid4().hex
            cache.set(CacheKeyPrefix.LOGIN_2FA.key(temp_token), user.pk, timeout=300)

            return {
                "temp_token": str(temp_token),
                "2fa_required": True,
            }
        
    authentication_classes = []
    serializer_class = LoginSerializer

    @extend_schema(
        summary="User login",
        description="Authenticates a user with username and password. If 2FA is enabled, it returns a temporary token for the second factor verification step.",
        request=LoginSerializer,
        responses={
            200: LoginSerializer,
            400: OpenApiResponse(description="Invalid credentials or input."),
        },
        tags=["Auth"],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class LoginTwoFAVerifyView(APIView):
    """
    Verifies the 2FA code after the initial login step.
    """

    authentication_classes = []

    class InputLoginTwoFAVerifySerializer(serializers.Serializer):
        temp_token = serializers.CharField(
            help_text="The temporary token received from the first login step."
        )
        code = serializers.CharField(
            max_length=6, help_text="The 6-digit code from the authenticator app."
        )

    class OutputLoginTwoFAVerifySerializer(serializers.Serializer):
        refresh = serializers.CharField()
        access = serializers.CharField()

    @extend_schema(
        summary="Verify 2FA code",
        description="Verifies the TOTP code using the temporary token from the login endpoint. Returns JWT tokens on success.",
        request=InputLoginTwoFAVerifySerializer,
        responses={
            200: OutputLoginTwoFAVerifySerializer,
            400: OpenApiResponse(description="Invalid or expired token/code."),
            404: OpenApiResponse(description="User not found."),
        },
        tags=["Auth", "2FA"],
    )
    def post(self, request):
        srz = self.InputLoginTwoFAVerifySerializer(data=request.data)
        srz.is_valid(raise_exception=True)
        data = srz.validated_data

        user_id = cache.get(CacheKeyPrefix.LOGIN_2FA.key(data["temp_token"]))
        if user_id is None:
            return Response(
                {"detail": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(User, id=user_id)

        if not verify_totp_code(user, data["code"]):
            return Response(
                {"detail": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)
        cache.delete(CacheKeyPrefix.LOGIN_2FA.key(data["temp_token"]))

        output_srz = self.OutputLoginTwoFAVerifySerializer(
            data={
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )
        return Response(output_srz.initial_data)


class TwoFASetupView(APIView):
    """
    Initiates the 2FA setup process for a user.
    """

    permission_classes = [IsAuthenticated]

    class OutputTwoFASetupSerializer(serializers.Serializer):
        secret = serializers.CharField(
            help_text="The secret key to be stored in the authenticator app."
        )
        otp_auth_url = serializers.CharField(
            help_text="A provisioning URI to be displayed as a QR code."
        )

    @extend_schema(
        summary="Setup 2FA",
        description="Generates a new TOTP secret and a provisioning URL for the authenticated user to set up 2FA.",
        request=None,
        responses={
            200: OutputTwoFASetupSerializer,
            400: OpenApiResponse(
                description="User has no email or 2FA is already enabled."
            ),
        },
        tags=["2FA"],
    )
    def post(self, request):
        user = request.user
        if not user.email:
            return Response(
                {"detail": "Email is required for 2FA setup."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.is_2fa_enabled:
            return Response(
                {"detail": "2FA is already active. To change it, reset it first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        secret = setup_totp_for_user(user)
        otp_auth_url = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email, issuer_name="Social-DJango"
        )

        srz = self.OutputTwoFASetupSerializer(
            data={"secret": secret, "otp_auth_url": otp_auth_url}
        )
        srz.is_valid()  # Should always be valid
        return Response(srz.data)


class TwoFAActivateView(APIView):
    """
    Activates 2FA for the user after they have scanned the QR code.
    """

    permission_classes = [IsAuthenticated]

    class InputTwoFAActivateSerializer(serializers.Serializer):
        code = serializers.CharField(
            max_length=6,
            help_text="The 6-digit code from the authenticator app to verify the setup.",
        )

    @extend_schema(
        summary="Activate 2FA",
        description="Verifies the initial TOTP code and activates 2FA for the user's account.",
        request=InputTwoFAActivateSerializer,
        responses={
            200: OpenApiResponse(description="2FA activated successfully."),
            400: OpenApiResponse(description="Invalid code or 2FA is already active."),
        },
        tags=["2FA"],
    )
    def post(self, request):
        if request.user.is_2fa_enabled:
            return Response(
                {"detail": "2FA is already active."}, status=status.HTTP_400_BAD_REQUEST
            )

        srz = self.InputTwoFAActivateSerializer(data=request.data)
        srz.is_valid(raise_exception=True)
        code = srz.validated_data["code"]

        if verify_totp_code(request.user, code):
            request.user.is_2fa_enabled = True
            request.user.save(update_fields=["is_2fa_enabled"])
            return Response({"detail": "2FA activated"})

        return Response({"detail": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)


class TwoFAResetRequestAPIView(APIView):
    """
    Requests a 2FA reset code to be sent to the user's email.
    """

    authentication_classes = []

    class InputTwoFAResetRequestSerializer(serializers.Serializer):
        username = serializers.CharField()

    @extend_schema(
        summary="Request 2FA reset",
        description="Sends a 2FA reset code to the user's registered email if 2FA is enabled for their account.",
        request=InputTwoFAResetRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="If the user exists and has 2FA enabled, a reset code has been sent to their email."
            )
        },
        tags=["2FA"],
    )
    def post(self, request):
        srz = self.InputTwoFAResetRequestSerializer(data=request.data)
        srz.is_valid(raise_exception=True)
        username = srz.validated_data["username"]

        try:
            user = User.objects.get(username=username)
            if user.is_2fa_enabled and user.email:
                code = get_random_string(6, allowed_chars="0123456789")
                cache.set(CacheKeyPrefix.RESET_2FA.key(username), code, timeout=600)
                send_mail(
                    "2FA Reset Code",
                    f"Your 2FA reset code is: {code}",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
        except User.DoesNotExist:
            # Fail silently to prevent user enumeration
            pass

        return Response(
            {
                "detail": "If your account exists and has 2FA enabled, a reset code was sent to your email."
            }
        )


class TwoFAResetConfirmAPIView(APIView):
    """
    Confirms the 2FA reset using the code sent via email.
    """

    authentication_classes = []

    class InputTwoFAResetConfirmSerializer(serializers.Serializer):
        username = serializers.CharField()
        code = serializers.CharField(max_length=6)

    @extend_schema(
        summary="Confirm 2FA reset",
        description="Resets and disables 2FA for a user account using the provided reset code.",
        request=InputTwoFAResetConfirmSerializer,
        responses={
            200: OpenApiResponse(description="2FA has been reset successfully."),
            400: OpenApiResponse(description="Invalid or expired code."),
        },
        tags=["2FA"],
    )
    def post(self, request):
        srz = self.InputTwoFAResetConfirmSerializer(data=request.data)
        srz.is_valid(raise_exception=True)
        data = srz.validated_data

        entry_key = CacheKeyPrefix.RESET_2FA.key(data["username"])
        cached_code = cache.get(entry_key)
        if not cached_code or cached_code != data["code"]:
            return Response(
                {"detail": "Invalid or expired code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(username=data["username"])
            user.totp_secret = None
            user.is_2fa_enabled = False
            user.save(update_fields=["totp_secret", "is_2fa_enabled"])
            cache.delete(entry_key)
            return Response({"detail": "2FA has been reset. You can set it up again."})
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired code."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TwoFAStatusAPIView(APIView):
    """
    Checks if 2FA is enabled for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    class OutputTwoFAStatusSerializer(serializers.Serializer):
        enabled = serializers.BooleanField()

    @extend_schema(
        summary="Get 2FA status",
        description="Returns the current 2FA status for the authenticated user.",
        responses={200: OutputTwoFAStatusSerializer},
        tags=["2FA"],
    )
    def get(self, request):
        srz = self.OutputTwoFAStatusSerializer(
            data={"enabled": request.user.is_2fa_enabled}
        )
        srz.is_valid()
        return Response(srz.data)


class PasswordResetRequestAPIView(APIView):
    """
    Requests a password reset code.
    """

    authentication_classes = []

    class InputPasswordResetRequestSerializer(serializers.Serializer):
        username = serializers.CharField()

    @extend_schema(
        summary="Request password reset",
        description="Sends a password reset code to the user's registered email.",
        request=InputPasswordResetRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="If the user exists, a reset code was sent to their email."
            )
        },
        tags=["Password"],
    )
    def post(self, request):
        srz = self.InputPasswordResetRequestSerializer(data=request.data)
        srz.is_valid(raise_exception=True)
        username = srz.validated_data["username"]
        try:
            user = User.objects.get(username=username)
            if user.email:
                send_password_reset_code(user)
        except User.DoesNotExist:
            pass  # Fail silently

        return Response(
            {
                "detail": "If the account exists, a reset code was sent to the associated email."
            }
        )


class PasswordResetConfirmAPIView(APIView):
    """
    Confirms the password reset with a code.
    """

    authentication_classes = []

    class InputPasswordResetConfirmSerializer(serializers.Serializer):
        email = serializers.EmailField()
        code = serializers.CharField(max_length=6)
        new_password = serializers.CharField()

    @extend_schema(
        summary="Confirm password reset",
        description="Sets a new password for a user using the reset code sent to their email.",
        request=InputPasswordResetConfirmSerializer,
        responses={
            200: OpenApiResponse(description="Password reset successful."),
            400: OpenApiResponse(description="Invalid or expired code."),
        },
        tags=["Password"],
    )
    def post(self, request):
        srz = self.InputPasswordResetConfirmSerializer(data=request.data)
        srz.is_valid(raise_exception=True)
        ok = reset_user_password_with_code(
            srz.validated_data["email"],
            srz.validated_data["code"],
            srz.validated_data["new_password"],
        )
        if ok:
            return Response({"detail": "Password reset successful."})
        return Response(
            {"detail": "Invalid or expired code."}, status=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetChangeAPIView(APIView):
    """
    Changes the password for an authenticated user.
    """

    permission_classes = [IsAuthenticated]

    class InputPasswordResetChangeSerializer(serializers.Serializer):
        old_password = serializers.CharField()
        new_password = serializers.CharField()

    @extend_schema(
        summary="Change password (authenticated)",
        description="Allows an authenticated user to change their password by providing their old and new password.",
        request=InputPasswordResetChangeSerializer,
        responses={
            200: OpenApiResponse(description="Password changed successfully."),
            400: OpenApiResponse(description="Old password is incorrect."),
        },
        tags=["Password"],
    )
    def post(self, request):
        srz = self.InputPasswordResetChangeSerializer(data=request.data)
        srz.is_valid(raise_exception=True)
        ok = change_user_password(
            request.user,
            srz.validated_data["old_password"],
            srz.validated_data["new_password"],
        )
        if ok:
            return Response({"detail": "Password changed."})
        return Response(
            {"detail": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST
        )


class EmailChangeRequestAPIView(APIView):
    """
    Requests an email change for an authenticated user.
    """

    permission_classes = [IsAuthenticated]

    class InputEmailChangeRequestSerializer(serializers.Serializer):
        new_email = serializers.EmailField()

    @extend_schema(
        summary="Request email change",
        description="Sends a confirmation link to the new email address to verify the change.",
        request=InputEmailChangeRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="Confirmation link sent to the new email address."
            )
        },
        tags=["Email"],
    )
    def post(self, request):
        srz = self.InputEmailChangeRequestSerializer(data=request.data)
        srz.is_valid(raise_exception=True)
        send_email_change_request(request.user, srz.validated_data["new_email"])
        return Response({"detail": "Confirmation link sent to new email."})


class EmailChangeConfirmAPIView(APIView):
    """
    Confirms an email change using a code.
    """

    permission_classes = [IsAuthenticated]

    class InputEmailChangeConfirmSerializer(serializers.Serializer):
        code = serializers.IntegerField()

    @extend_schema(
        summary="Confirm email change",
        description="Confirms the email change for the authenticated user using the provided code.",
        request=InputEmailChangeConfirmSerializer,
        responses={
            200: OpenApiResponse(description="Email changed successfully."),
            400: OpenApiResponse(description="Invalid or expired code/link."),
        },
        tags=["Email"],
    )
    def post(self, request):
        srz = self.InputEmailChangeConfirmSerializer(data=request.data)
        srz.is_valid(raise_exception=True)
        ok = confirm_email_change(request.user, srz.validated_data["code"])
        if ok:
            return Response({"detail": "Email changed."})
        return Response(
            {"detail": "Invalid or expired link."}, status=status.HTTP_400_BAD_REQUEST
        )
