from django.urls import path
from .views import (
    ConnectToUserAPIView,
    AcceptConnectionAPIView,
    RejectConnectionAPIView,
)


urlpatterns = [
    path("request/", ConnectToUserAPIView.as_view(), name="request"),
    path("accept/", AcceptConnectionAPIView.as_view(), name="accept"),
    path("reject/", RejectConnectionAPIView.as_view(), name="reject"),
]
