from apps.comment.models import Comment
from django.db.models import Count

def list_comments(content_id):
    return (
        Comment.objects.filter(content_id=content_id, reply__isnull=True)
        .select_related('user')
        .annotate(count_replies=Count('replies'), count_likes=Count('likes'))
    )

def list_replies(content_id, comment_id):
    return (
        Comment.objects.filter(content_id=content_id, reply_id=comment_id)
        .select_related('user')
        .annotate(count_replies=Count('replies'), count_likes=Count('likes'))
    )

def get_comment_with_counts(comment_id):
    return (
        Comment.objects.filter(pk=comment_id)
        .select_related('user')
        .annotate(count_replies=Count('replies'), count_likes=Count('likes'))
        .first()
    )