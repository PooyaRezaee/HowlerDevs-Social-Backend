from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema
from .services import create_comment, delete_comment
from .selectors import list_comments, list_replies, get_comment_with_counts
from .serializers import CommentSerializer, CommentCreateSerializer
from .permissions import IsCommentOwner
from apps.comment.models import Comment


class CommentListCreateAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    @extend_schema(request=CommentCreateSerializer, responses=CommentSerializer(many=True), auth=[])
    def get(self, request, content_id):
        comments = list_comments(content_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @extend_schema(request=CommentCreateSerializer, responses=CommentSerializer)
    def post(self, request, content_id):
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = create_comment(
            user=request.user,
            content_id=content_id,
            text=serializer.validated_data["text"],
            reply_id=serializer.validated_data.get("reply"),
        )
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class CommentDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCommentOwner]

    def delete(self, request, pk):
        comment = Comment.objects.filter(pk=pk).first()
        if not comment:
            return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, comment)
        delete_comment(comment)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReplyListAPIView(APIView):
    authentication_classes = []

    @extend_schema(responses=CommentSerializer(many=True))
    def get(self, request, content_id, comment_id):
        replies = list_replies(content_id, comment_id)
        serializer = CommentSerializer(replies, many=True)
        return Response(serializer.data)


class CommentLikeToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: CommentSerializer})
    def post(self, request, comment_id):
        comment = get_comment_with_counts(comment_id)
        if not comment:
            return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
            liked = False
        else:
            comment.likes.add(request.user)
            liked = True

        return Response({"liked": liked}, status=status.HTTP_200_OK)