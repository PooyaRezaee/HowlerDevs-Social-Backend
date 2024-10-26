from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Post, Reel
from .base_view import *
from .serializers import (
    PostOutPutSerializer,
    ReelOutPutSerializer,
    PostInputSerializer,
    ReelInputSerializer,
    ContentUpdateInputSerializer
)

# Separate post and reels view
class UserPostListAPIView(UserContentListAPIView):
    model = Post
    serializer_class = PostOutPutSerializer


class UserReelListAPIView(UserContentListAPIView):
    model = Reel
    serializer_class = ReelOutPutSerializer


class RecommendPostAPIView(RecommendContentAPIView):
    model = Post

@extend_schema_view(
    summary="create a post",
    post=extend_schema(
        request=PostInputSerializer,
        responses={200: PostOutPutSerializer}
    )
)
class CreatePostAPIView(CreateContentAPIView):
    model = Post
    input_serializer_class = PostInputSerializer
    output_serializer_class = PostOutPutSerializer

@extend_schema_view(
    summary="create a reel",
    post=extend_schema(
        request=ReelInputSerializer,
        responses={200: ReelOutPutSerializer}
    )
)
class CreateReelAPIView(CreateContentAPIView):
    model = Reel
    input_serializer_class = ReelInputSerializer
    output_serializer_class = ReelOutPutSerializer
from drf_spectacular.types import OpenApiTypes

@extend_schema_view(
    patch=extend_schema(
        summary="update a post",
        description="update a post(just description field). Only the owner can update the post.",
        request=ContentUpdateInputSerializer,
        responses={200: PostOutPutSerializer}
    ),
    delete=extend_schema(
        summary="Delete a post",
        description="Delete a post. Only the owner can delete the post.",
        responses={
            204: None,
        },
    )
)
class UpdateDeletePostAPIView(UpdateDeleteContentAPIView):
    model = Post
    input_serializer_class = ContentUpdateInputSerializer
    output_serializer_class = PostOutPutSerializer

@extend_schema_view(
    patch=extend_schema(
        summary="update a reel",
        description="update a reel(just description field). Only the owner can update the reel.",
        request=ContentUpdateInputSerializer,
        responses={200: ReelOutPutSerializer}
    ),
    delete=extend_schema(
        summary="Delete a reel",
        description="Delete a reel. Only the owner can delete the reel.",
        responses={
            204: None,
        },
    )
)
class UpdateDeleteReelAPIView(UpdateDeleteContentAPIView):
    model = Reel
    input_serializer_class = ContentUpdateInputSerializer
    output_serializer_class = PostOutPutSerializer


class SearchPostsAPIView(SearchContentAPIView):
    model = Post


class SearchReelsAPIView(SearchContentAPIView):
    model = Reel


class ExplorePostsAPIView(ExploreAPIView):
    model = Post


class ExploreReelsAPIView(ExploreAPIView):
    model = Reel
