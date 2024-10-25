from django.urls import path
from .views import UserContentAPIView

urlpatterns = [
    path("", UserContentAPIView.as_view(), name="user-content"),
]
