from apps.comment.models import Comment
from apps.content.models import Content
from django.shortcuts import get_object_or_404

def create_comment(user, content_id, text, reply_id=None):
    content = get_object_or_404(Content, pk=content_id)
    reply = Comment.objects.filter(pk=reply_id).first() if reply_id else None
    return Comment.objects.create(user=user, content=content, text=text, reply=reply)

def delete_comment(comment):
    comment.delete()