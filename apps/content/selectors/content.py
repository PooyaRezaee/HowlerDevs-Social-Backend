from apps.account.models import User
from apps.connect.selectors.connection import list_connections
from ..models import Post, MediaContent,Content


def get_post_by_id(post_id: int) -> Post:
    return Post.objects.filter(id=post_id).first()


def get_media_content_by_id(mc_id: int) -> MediaContent:
    return MediaContent.objects.filter(id=mc_id).first()


def get_posts_by_owner(username: str) -> Post:
    return Post.objects.filter(owner__username=username)


def get_media_content_by_owner(username: str) -> MediaContent:
    return MediaContent.objects.filter(owner__username=username)


def get_content_by_owner(username: str) -> list[Content]:
    contents = Content.objects.filter(owner__username=username)
    return contents


# TODO create type content
# TODO get content in argument instead create function for each them (for top functions)
def get_connection_content(user: User):
    connected_users = list_connections(user)
    return Content.objects.filter(owner_in=connected_users).order_by("-created_at").select_related("post","mediacontent") # TODO check select realted


def get_contents_by_owner(username: str):
    return Content.objects.filter(owner__username=username)