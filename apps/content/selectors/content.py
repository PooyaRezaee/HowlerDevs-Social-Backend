from apps.account.models import User
from ..models import Post, Reel


def get_post_by_id(post_id: int) -> Post:
    return Post.objects.filter(id=post_id).first()


def get_reel_by_id(reel_id: int) -> Reel:
    return Reel.objects.filter(id=reel_id).first()


def get_posts_by_owner(username: str) -> Post:
    return Post.objects.filter(owner__username=username)


def get_reels_by_owner(username: str) -> Reel:
    return Reel.objects.filter(owner__username=username)


def get_content_by_owner(username: str) -> dict[str, Post | Reel]:
    posts = Post.objects.filter(owner__username=username)
    reels = Reel.objects.filter(owner__username=username)
    return {"posts": posts, "reels": reels}
