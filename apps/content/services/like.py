from django.shortcuts import get_object_or_404
from apps.account.models import User
from ..models import Content


def like_content(user: User, content_id: int):
    content = get_object_or_404(Content, id=content_id)
    content.likes.add(user)
    return content


def unlike_content(user: User, content_id: int):
    content = get_object_or_404(Content, id=content_id)
    content.likes.remove(user)
    return content