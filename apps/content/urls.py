from django.urls import path
from .views import (
    UserPostListAPIView,
    UserReelListAPIView,
    SearchPostsAPIView,
    SearchReelsAPIView,
    CreateReelAPIView,
    CreatePostAPIView,
    UpdateDeleteReelAPIView,
    UpdateDeletePostAPIView,
    RecommendPostAPIView,
    ExplorePostsAPIView,
    ExploreReelsAPIView,
)

urlpatterns = [
    path("user/posts/<str:username>/", UserPostListAPIView.as_view(), name="user-post"),
    path("user/reels/<str:username>/", UserReelListAPIView.as_view(), name="user-reel"),
    path("post/", CreatePostAPIView.as_view(), name="create-post"),
    path("reel/", CreateReelAPIView.as_view(), name="create-reel"),
    path(
        "post/<int:pk>/", UpdateDeletePostAPIView.as_view(), name="update-delete-post"
    ),
    path(
        "reel/<int:pk>/", UpdateDeleteReelAPIView.as_view(), name="update-delete-reel"
    ),
    path("posts/search/", SearchPostsAPIView.as_view(), name="search-post"),
    path("reels/search/", SearchReelsAPIView.as_view(), name="search-reel"),
    # path("posts/recommend/", RecommendPostAPIView.as_view(), name="recommend-post"),
    # path("posts/explore/", ExplorePostsAPIView.as_view(), name="explore-post"),
    # path("reels/explore/", ExploreReelsAPIView.as_view(), name="explore-reel"),
    # path("post/like/", ExploreReelsAPIView.as_view(), name="explore-reel"),
    # path("reels/like/", ExploreReelsAPIView.as_view(), name="explore-reel"),
    # path("post/unlike/", ExploreReelsAPIView.as_view(), name="explore-reel"),
    # path("reels/unlike/", ExploreReelsAPIView.as_view(), name="explore-reel"),
]
