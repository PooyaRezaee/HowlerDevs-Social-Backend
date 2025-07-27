from django.urls import path
from .views import (
    UserPostListAPIView,
    UserMediaListAPIView,
    UserContentListAPIView,
    CreatePostAPIView,
    CreateMediaContentAPIView,
    UpdateDeletePostAPIView,
    UpdateDeleteMediaAPIView,
    ContentSearchAPIView,
    HashtagSearchPostsAPIView,
    HashtagSearchMediaContentsAPIView,
    ExploreContentAPIView,
    RecommendContentAPIView,
    LikeContentAPIView,
    UnLikeContentAPIView,
)

urlpatterns = [
    path("user/posts/<str:username>/", UserPostListAPIView.as_view(), name="user-post"),
    path(
        "user/media/<str:username>/",
        UserMediaListAPIView.as_view(),
        name="user-media",
    ),
    path("user/contents/<str:username>/", UserContentListAPIView.as_view(), name="user-content"),
    path("post/", CreatePostAPIView.as_view(), name="create-post"),
    path("media/", CreateMediaContentAPIView.as_view(), name="create-media"),
    path(
        "post/<int:pk>/", UpdateDeletePostAPIView.as_view(), name="update-delete-post"
    ),
    path(
        "media/<int:pk>/",
        UpdateDeleteMediaAPIView.as_view(),
        name="update-delete-media",
    ),
    path("search/", ContentSearchAPIView.as_view(), name="content-search"),
    path(
        "post/search/hashtag/",
        HashtagSearchPostsAPIView.as_view(),
        name="hashtag-search-post",
    ),
    path(
        "media/search/hashtag/",
        HashtagSearchMediaContentsAPIView.as_view(),
        name="hashtag-search-media",
    ),
    path('posts/explore/', ExploreContentAPIView.as_view(), name='explore-content'),
    path('posts/recommend/', RecommendContentAPIView.as_view(), name='recommend-content'),
    path('content/like/', LikeContentAPIView.as_view(), name='content-like'),
    path('content/unlike/', UnLikeContentAPIView.as_view(), name='content-unlike'),
]
