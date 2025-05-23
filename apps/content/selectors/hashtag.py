from typing import Optional
from django.db.models import QuerySet
from ..models import Hashtag, Content, Post, MediaContent


def get_hashtag_by_name(name: str) -> Hashtag | None:
    return Hashtag.objects.filter(name=name).first()


def get_posts_by_hashtag(hashtag_name: str) -> QuerySet | None:
    hashtag = get_hashtag_by_name(hashtag_name)
    if hashtag:
        return Post.objects.filter(id__in=hashtag.contents.values_list('id', flat=True))
    return None


def get_media_contents_by_hashtag(hashtag_name: str) -> QuerySet | None:
    hashtag = get_hashtag_by_name(hashtag_name)
    if hashtag:
        return MediaContent.objects.filter(id__in=hashtag.contents.values_list('id', flat=True))
    return None


def get_contents_by_hashtag(hashtag_name: str) -> QuerySet | None:
    hashtag = get_hashtag_by_name(hashtag_name)
    if hashtag:
        return Content.objects.filter(id__in=hashtag.contents.values_list('id', flat=True))
    return None
