from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (
    RegisterAPIView, ProfileUpdateAPIView, ProfileRetrieveAPIView, ProfileAvatarUpdateAPIView,
    LoginView, LoginTwoFAVerifyView,
    PasswordResetRequestAPIView, PasswordResetConfirmAPIView, PasswordResetChangeAPIView,
    EmailChangeRequestAPIView, EmailChangeConfirmAPIView, TwoFAStatusAPIView, TwoFAActivateView, TwoFASetupView, TwoFAResetRequestAPIView, TwoFAResetConfirmAPIView
)


urlpatterns = [
    path(
        "jwt/",
        include(
            (
                [
                    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
                    path("verify/", TokenVerifyView.as_view(), name="verify"),
                    path('login/', LoginView.as_view(), name='jwt_login'),
                    path('2fa/verify/', LoginTwoFAVerifyView.as_view(), name='jwt_2fa_verify'),
                ],
                "jwt",
            )
        ),
    ),
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("update/info/", ProfileUpdateAPIView.as_view(), name="edit"),
    path("update/avatar/", ProfileAvatarUpdateAPIView.as_view(), name="edit"),

    path("password/reset/request/", PasswordResetRequestAPIView.as_view(), name="password_reset_request"),
    path("password/reset/confirm/", PasswordResetConfirmAPIView.as_view(), name="password_reset_confirm"),
    path("password/change/", PasswordResetChangeAPIView.as_view(), name="password_reset_change"),

    path("email/change/request/", EmailChangeRequestAPIView.as_view(), name="email_change_request"),
    path("email/change/confirm/", EmailChangeConfirmAPIView.as_view(), name="email_change_confirm"),

    path("2fa/status/", TwoFAStatusAPIView.as_view(), name="2fa_status"),
    path("2fa/setup/request/", TwoFASetupView.as_view(), name="2fa_setup"),
    path("2fa/setup/activate/", TwoFAActivateView.as_view(), name="2fa_activate"),

    path("2fa/reset/request/", TwoFAResetRequestAPIView.as_view(), name="2fa_reset_request"),
    path("2fa/reset/confirm/", TwoFAResetConfirmAPIView.as_view(), name="2fa_reset_confirm"),

    path("detail/<str:username>/", ProfileRetrieveAPIView.as_view(), name="profile_detail"),
]
