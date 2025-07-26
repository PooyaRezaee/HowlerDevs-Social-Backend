from django.urls import path
from .views import (
    ConnectToUserAPIView,
    AcceptConnectionAPIView,
    RejectConnectionAPIView,
    ConnectionListAPIView,
    RequestConnectionListSentAPIView,
    RequestConnectionListReceivedAPIView,
    ConnectionRemoveAPIView,
)


urlpatterns = [
    path("request/", ConnectToUserAPIView.as_view(), name="request"),
    path("accept/", AcceptConnectionAPIView.as_view(), name="request-accept"),
    path("reject/", RejectConnectionAPIView.as_view(), name="request-reject"),
    path("list/", ConnectionListAPIView.as_view(), name="list"),
    path("remove/", ConnectionRemoveAPIView.as_view(), name="remove"),
    path(
        "request/sent/", RequestConnectionListSentAPIView.as_view(), name="request-sent"
    ),
    path(
        "request/receiver/",
        RequestConnectionListReceivedAPIView.as_view(),
        name="request-reciever",
    ),
]
