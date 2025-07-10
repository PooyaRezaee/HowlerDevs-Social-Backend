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
    # path("posts/recommend/", RecommendPostAPIView.as_view(), name="recommend-post"),
    # path("posts/explore/", ExplorePostsAPIView.as_view(), name="explore-post"),
    # path("reels/explore/", ExploreReelsAPIView.as_view(), name="explore-reel"),
    # path("post/like/", ExploreReelsAPIView.as_view(), name="explore-reel"),
    # path("reels/like/", ExploreReelsAPIView.as_view(), name="explore-reel"),
    # path("post/unlike/", ExploreReelsAPIView.as_view(), name="explore-reel"),
    # path("reels/unlike/", ExploreReelsAPIView.as_view(), name="explore-reel"),
]
