from apps.account.models import User
from ..models import Post, Reel


def get_post_by_id(post_id: int) -> Post:
    return Post.objects.filter(id=post_id).first()


def get_reel_by_id(reel_id: int) -> Reel:
    return Reel.objects.filter(id=reel_id).first()


def get_posts_by_owner(user: User) -> Post:
    return Post.objects.filter(user=user)


def get_reels_by_owner(user: User) -> Reel:
    return Reel.objects.filter(user=user)


def get_content_by_owner(user: User) -> dict[str, Post | Reel]:
    posts = Post.objects.filter(owner=user)
    reels = Reel.objects.filter(owner=user)
    return {"posts": posts, "reels": reels}
