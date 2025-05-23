from typing import Optional
from django.db.models import QuerySet
from django.contrib.postgres.search import TrigramSimilarity
from apps.content.models import Content, Post, MediaContent


def search_contents(query: Optional[str] = None, content_type: Optional[str] = None, hashtag: Optional[str] = None) -> QuerySet:
    if content_type == "post":
        qs = Post.objects.all()
    elif content_type == "media":
        qs = MediaContent.objects.all()
    else:
        qs = Content.objects.all()

    if hashtag:
        qs = qs.filter(hashtags__name__iexact=hashtag)

    if query:
        qs = qs.annotate(similarity=TrigramSimilarity("description", query))\
               .filter(similarity__gt=0.11)\
               .order_by("-similarity")

    return qs