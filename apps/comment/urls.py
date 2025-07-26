from django.urls import path
from .views import CommentListCreateAPIView, CommentDeleteAPIView, ReplyListAPIView, CommentLikeToggleAPIView

urlpatterns = [
    path("content/<int:content_id>/", CommentListCreateAPIView.as_view(), name="comment-list-create"),
    path("<int:pk>/delete/", CommentDeleteAPIView.as_view(), name="comment-delete"),
    path("content/<int:content_id>/comment/<int:comment_id>/replies/", ReplyListAPIView.as_view(), name="comment-replies"),
    path("<int:comment_id>/like-toggle/", CommentLikeToggleAPIView.as_view(), name="comment-like-toggle"),
]