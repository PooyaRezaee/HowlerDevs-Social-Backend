from typing import Any
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Post, Reel
from .selectors.content import (
    get_posts_by_owner,
    get_reels_by_owner,
    get_connection_content,
)
from .selectors.hashtag import get_reels_by_hashtag, get_posts_by_hashtag
from .services.content import (
    create_post,
    create_reel,
    update_post,
    update_reel,
    delete_post,
    delete_reel,
)
from .permissions import IsContentOwner

__all__ = [
    "UserContentListAPIView",
    "CreateContentAPIView",
    "UpdateDeleteContentAPIView",
    "SearchContentAPIView",
    "RecommendContentAPIView",
    "ExploreAPIView",
]


class UserContentListAPIView(APIView):
    model = None
    serializer_class = None

    def get(self, request, username):
        if self.model is Post:
            contents = get_posts_by_owner(username)
        else:
            contents = get_reels_by_owner(username)

        srz = self.serializer_class(contents, many=True)
        return Response(srz.data)


class CreateContentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = None
    input_serializer_class = None
    output_serializer_class = None

    def post(self, request):
        srz = self.input_serializer_class(data=request.data)
        srz.is_valid(raise_exception=True)
        srz_data = srz.validated_data
        if self.model is Post:
            content = create_post(
                owner=request.user,
                description=srz_data["description"],
                thumbnail=srz_data.get("thumbnail"),
            )
        else:
            content = create_reel(
                owner=request.user,
                description=srz_data["description"],
                thumbnail=srz_data.get("thumbnail"),
                video=srz_data.get("video"),
                sound=srz_data.get("sound"),
            )

        return Response(self.output_serializer_class(content).data)


class UpdateDeleteContentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsContentOwner]
    model = None
    input_serializer_class = None
    output_serializer_class = None

    def get_object(self, pk):
        obj = get_object_or_404(self.model, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_update_function(self):
        if self.model is Post:
            return update_post
        else:
            return update_reel

    def get_delete_function(self):
        if self.model is Post:
            return delete_post
        else:
            return delete_reel

    def patch(self, request, pk):
        content_obj = self.get_object(pk)

        srz = self.input_serializer_class(data=request.data)
        srz.is_valid(raise_exception=True)
        srz_data = srz.validated_data

        update_func = self.get_update_function()
        updated_content = update_func(
            content_obj, description=srz_data.get("description")
        )

        return Response(self.output_serializer_class(updated_content).data)

    def delete(self, request, pk):
        content_obj = self.get_object(pk)
        delete_func = self.get_delete_function()
        delete_func(content_obj)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SearchContentAPIView(APIView):
    model = None
    serializer_class = None

    def get_queryset(self, hashtag_name):
        if self.model is Post:
            return get_posts_by_hashtag(hashtag_name)
        else:
            return get_reels_by_hashtag(hashtag_name)

    def get(self, request):
        search_query = self.request.GET.get("q", None)
        contents = self.get_queryset(search_query)

        if contents:
            srz = self.serializer_class(contents, many=True)
            return Response(srz.data)

        return Response(status=status.HTTP_204_NO_CONTENT)


class RecommendContentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = None
    serializer_class = None

    def get(self, request):
        contents = get_connection_content(request.user, self.model)
        srz = self.serializer_class(contents, many=True)
        return Response(srz.data)


class ExploreAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pass
