from apps.account.models import User
from apps.connect.selectors.connection import list_connections
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


# TODO create type content
# TODO get content in argument instead create function for each them (for top functions)
def get_connection_content(user: User, content: Post | Reel):
    connected_users = list_connections(user)
    return content.objects.filter(owner_in=connected_users).order_by("-created_at")
