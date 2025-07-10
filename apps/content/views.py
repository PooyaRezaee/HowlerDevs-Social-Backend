from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    OpenApiParameter,
)
from .models import Post, MediaContent, Content
from .base_view import (
    UserContentListAPIView,
    CreateContentAPIView,
    UpdateDeleteContentAPIView,
    SearchContentAPIView,
)
from .serializers import (
    PostInputSerializer,
    PostOutputSerializer,
    MediaContentInputSerializer,
    MediaContentOutputSerializer,
    PostInputSerializer,
    ContentUpdateInputSerializer,
    ContentOutputSerializer,
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from apps.content.selectors.search import search_contents


@extend_schema_view(
    get=extend_schema(
        summary="get user's posts",
    )
)
class UserPostListAPIView(UserContentListAPIView):
    model = Post
    serializer_class = PostOutputSerializer
    authentication_classes = []


@extend_schema_view(
    get=extend_schema(
        summary="get user's media contents",
    )
)
class UserMediaListAPIView(UserContentListAPIView):
    model = MediaContent
    serializer_class = MediaContentOutputSerializer
    authentication_classes = []


@extend_schema_view(
    get=extend_schema(
        summary="get user's all content",
        description="In the case of capturing all user content, there is less detail in the response.",
    )
)
class UserContentListAPIView(UserContentListAPIView):
    model = Content
    serializer_class = ContentOutputSerializer
    authentication_classes = []


@extend_schema_view(
    post=extend_schema(
        summary="create a post",
        request=PostInputSerializer,
        responses={200: PostOutputSerializer},
    ),
)
class CreatePostAPIView(CreateContentAPIView):
    model = Post
    input_serializer_class = PostInputSerializer
    output_serializer_class = PostOutputSerializer
    authentication_classes = []


@extend_schema_view(
    post=extend_schema(
        description="media_type must be video or audio",
        summary="create a media content",
        request=MediaContentInputSerializer,
        responses={200: MediaContentOutputSerializer},
    ),
)
class CreateMediaContentAPIView(CreateContentAPIView):
    model = MediaContent
    input_serializer_class = MediaContentInputSerializer
    output_serializer_class = MediaContentOutputSerializer


@extend_schema_view(
    patch=extend_schema(
        summary="update a post",
        description="update a post(just description field). Only the owner can update the post.",
        request=ContentUpdateInputSerializer,
        responses={200: PostOutputSerializer},
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
    output_serializer_class = PostOutputSerializer


@extend_schema_view(
    patch=extend_schema(
        summary="update a media content",
        description="update a media content(just description field). Only the owner can update the media content.",
        request=ContentUpdateInputSerializer,
        responses={200: MediaContentOutputSerializer},
    ),
    delete=extend_schema(
        summary="Delete a media content",
        description="Delete a media content. Only the owner can delete the media.",
        responses={
            204: None,
        },
    ),
)
class UpdateDeleteMediaAPIView(UpdateDeleteContentAPIView):
    model = MediaContent
    input_serializer_class = ContentUpdateInputSerializer
    output_serializer_class = MediaContentOutputSerializer


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
                response=PostOutputSerializer, description="List of posts found"
            ),
            204: OpenApiResponse(description="No posts found for the provided hashtag"),
        },
    )
)
class HashtagSearchPostsAPIView(SearchContentAPIView):
    model = Post
    serializer_class = PostOutputSerializer
    authentication_classes = []


@extend_schema_view(
    get=extend_schema(
        summary="Search media contents by hashtag",
        description="Retrieve a list of media contents that match the specified hashtag",
        parameters=[
            OpenApiParameter(
                "q", description="Hashtag to search for", required=True, type=str
            )
        ],
        responses={
            200: OpenApiResponse(
                response=MediaContentOutputSerializer,
                description="List of media contents found",
            ),
            204: OpenApiResponse(
                description="No media contents found for the provided hashtag"
            ),
        },
    )
)
class HashtagSearchMediaContentsAPIView(SearchContentAPIView):
    authentication_classes = []

    model = MediaContent
    serializer_class = MediaContentOutputSerializer


@extend_schema_view(
    get=extend_schema(
        summary="Search contents",
        description="Search for contents (posts or media) using query string, type, and hashtag filters.",
        parameters=[
            OpenApiParameter(
                name="q",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="The search query string",
            ),
            OpenApiParameter(
                name="type",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Content type to search for: 'post', 'media', or omit for all types",
            ),
            OpenApiParameter(
                name="hashtag",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter contents by a specific hashtag",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=ContentOutputSerializer,
                description="List of matching contents",
            ),
            204: OpenApiResponse(description="No content found matching the criteria"),
        },
    )
)
class ContentSearchAPIView(APIView):
    authentication_classes = []

    def get(self, request):
        query = request.query_params.get("q")
        content_type = request.query_params.get("type")  # post | media | None
        hashtag = request.query_params.get("hashtag")
        queryset = search_contents(
            query=query, content_type=content_type, hashtag=hashtag
        )

        return Response(
            ContentOutputSerializer(queryset, many=True).data, status=status.HTTP_200_OK
        )
