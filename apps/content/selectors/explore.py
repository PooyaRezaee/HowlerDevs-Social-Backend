import random
from datetime import timedelta
from itertools import chain
from django.utils import timezone
from apps.connect.models import Connection
from django.db.models import (
    Count,
    Q,
    F,
    Case,
    When,
    Value,
    IntegerField,
    Subquery,
    Exists,
)
from ..models import Content, Hashtag


def trending_content(limit: int = 20):
    one_week_ago = timezone.now() - timedelta(days=7)
    return (
        Content.objects.filter(created_at__gte=one_week_ago)
        .annotate(like_count=Count("likes"))
        .select_related("owner")
        .prefetch_related("hashtags")
        .order_by("-like_count")[:limit]
    )


def related_content(user, limit: int = 20):
    tags = Hashtag.objects.filter(contents__likes=user).distinct()
    return (
        Content.objects.filter(hashtags__in=tags)
        .exclude(Q(owner=user) | Q(likes=user))
        .annotate(like_count=Count("likes"))
        .select_related("owner")
        .prefetch_related("hashtags")
        .distinct()[:limit]
    )


def recommend_content(user, limit: int = 20):
    conns = Connection.objects.accepted_with(user).values_list(
        "requester_id", "receiver_id"
    )
    peer_ids = set(chain.from_iterable(conns)) - {user.id}
    return (
        Content.objects.filter(owner_id__in=peer_ids)
        .annotate(like_count=Count("likes"))
        .select_related("owner")
        .prefetch_related("hashtags")
        .order_by("-created_at")[:limit]
    )




def explore_content(user, limit=3):
    """
    It calculates a score for recent content based on a weighted combination of
    overall popularity (likes), social relevance (likes by the user's connections),
    and personal interest (common hashtags with previously liked content).
    The function returns a QuerySet of the highest-scoring Content objects.

    this code optimized with gemini2.5 pro
    """
    now = timezone.now()
    week_ago = now - timedelta(days=7)

    # --- Step 1: Pre-fetch IDs for efficient subqueries ---

    # Get IDs of the user's accepted connections (friends)
    user_connections = Connection.objects.accepted_with(user)
    friend_ids = [
        c.requester_id if c.receiver_id == user.id else c.receiver_id
        for c in user_connections
    ]

    # Get a QuerySet of hashtag IDs that the user has previously liked
    liked_hashtags_qs = Hashtag.objects.filter(contents__likes=user).distinct()

    # --- Step 2: Build the main QuerySet with annotations for scoring ---

    # Start with a base of recent, relevant content
    base_query = (
        Content.objects.filter(
            created_at__gte=week_ago,
            owner__is_active=True,
            owner__is_private=False,
        )
        .exclude(owner=user)  # Exclude user's own content
        .exclude(likes=user)  # Exclude content already liked by the user
    )

    # Annotate with scores
    scored_content = base_query.annotate(
        # 1. Like Score: Each like is worth 2 points
        like_score=Count("likes") * 2,

        # 2. Recency Score: Based on creation time
        recency_score=Case(
            When(created_at__gte=now - timedelta(days=1), then=Value(15)),
            When(created_at__gte=now - timedelta(days=3), then=Value(8)),
            default=Value(3),
            output_field=IntegerField(),
        ),

        # 3. Social Score: Boost posts liked by friends. Each friend's like is worth 10 points.
        social_score=Count("likes", filter=Q(likes__id__in=friend_ids)) * 10,

        # 4. Interest Score: Boost posts with hashtags the user has liked before.
        # Uses a high-performance EXISTS subquery.
        interest_score=Case(
            When(
                Exists(
                    # Check if any of the post's hashtags are in the user's liked hashtags
                    Hashtag.objects.filter(
                        id__in=Subquery(liked_hashtags_qs.values('id')),
                        contents__id=F('id')
                    )
                ),
                then=Value(20),
            ),
            default=Value(0),
            output_field=IntegerField(),
        ),

        # 5. Total Score: Sum of all scores
        total_score=F("like_score")
        + F("recency_score")
        + F("social_score")
        + F("interest_score"),
    )

    # --- Step 3: Finalize the query ---
    final_results = (
        scored_content.filter(total_score__gt=0)  # Only get posts with a positive score
        .order_by("-total_score", "-created_at")  # Order by score, then by date
        .select_related("owner")  # Optimize by pre-fetching owner details
        .prefetch_related("hashtags")  # Optimize by pre-fetching hashtags
        [:limit]  # Get the top N results
    )

    return final_results