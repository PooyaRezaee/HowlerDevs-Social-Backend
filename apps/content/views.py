from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    OpenApiParameter,
)
from .models import Post, Reel
from .base_view import *
from .serializers import (
    PostOutPutSerializer,
    ReelOutPutSerializer,
    PostInputSerializer,
    ReelInputSerializer,
    ContentUpdateInputSerializer,
)


# Separate post and reels view


@extend_schema_view(
    get=extend_schema(
        summary="get user's posts",
    )
)
class UserPostListAPIView(UserContentListAPIView):
    model = Post
    serializer_class = PostOutPutSerializer


@extend_schema_view(
    get=extend_schema(
        summary="get user's reels",
    )
)
class UserReelListAPIView(UserContentListAPIView):
    model = Reel
    serializer_class = ReelOutPutSerializer


class RecommendPostAPIView(RecommendContentAPIView):
    model = Post


@extend_schema_view(
    post=extend_schema(
        summary="create a post",
        request=PostInputSerializer,
        responses={200: PostOutPutSerializer},
    ),
)
class CreatePostAPIView(CreateContentAPIView):
    model = Post
    input_serializer_class = PostInputSerializer
    output_serializer_class = PostOutPutSerializer


@extend_schema_view(
    post=extend_schema(
        summary="create a reel",
        request=ReelInputSerializer,
        responses={200: ReelOutPutSerializer},
    ),
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
        responses={200: PostOutPutSerializer},
    ),
    delete=extend_schema(
        summary="Delete a post",
        description="Delete a post. Only the owner can delete the post.",
        responses={
            204: None,
        },
    ),
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
        responses={200: ReelOutPutSerializer},
    ),
    delete=extend_schema(
        summary="Delete a reel",
        description="Delete a reel. Only the owner can delete the reel.",
        responses={
            204: None,
        },
    ),
)
class UpdateDeleteReelAPIView(UpdateDeleteContentAPIView):
    model = Reel
    input_serializer_class = ContentUpdateInputSerializer
    output_serializer_class = PostOutPutSerializer


@extend_schema_view(
    get=extend_schema(
        summary="Search posts by hashtag",
        description="Retrieve a list of posts that match the specified hashtag",
        parameters=[
            OpenApiParameter(
                "q", description="Hashtag to search for", required=True, type=str
            )
        ],
        responses={
            200: OpenApiResponse(
                response=PostOutPutSerializer, description="List of posts found"
            ),
            204: OpenApiResponse(description="No posts found for the provided hashtag"),
        },
    )
)
class SearchPostsAPIView(SearchContentAPIView):
    model = Post
    serializer_class = PostOutPutSerializer


@extend_schema_view(
    get=extend_schema(
        summary="Search reels by hashtag",
        description="Retrieve a list of reels that match the specified hashtag",
        parameters=[
            OpenApiParameter(
                "q", description="Hashtag to search for", required=True, type=str
            )
        ],
        responses={
            200: OpenApiResponse(
                response=ReelOutPutSerializer, description="List of reels found"
            ),
            204: OpenApiResponse(description="No reels found for the provided hashtag"),
        },
    )
)
class SearchReelsAPIView(SearchContentAPIView):
    model = Reel
    serializer_class = ReelOutPutSerializer


class ExplorePostsAPIView(ExploreAPIView):
    model = Post


class ExploreReelsAPIView(ExploreAPIView):
    model = Reel
