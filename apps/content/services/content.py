from apps.account.models import User
from ..models import Post, Reel
from .hashtag import link_hashtags_to_content, unlink_hashtags_from_content


def create_post(owner: User, description: str, thumbnail=None) -> Post:
    post = Post.objects.create(
        owner=owner, description=description, thumbnail=thumbnail
    )
    link_hashtags_to_content(post)

    return post


def update_post(post: Post, description: str = None) -> Post:
    if description:
        unlink_hashtags_from_content(post)
        post.description = description
        link_hashtags_to_content(post)

    post.save()
    return post


def delete_post(post: Post) -> None:
    unlink_hashtags_from_content(post)
    post.delete()


def create_reel(
    owner: User, description: str, video=None, sound=None, thumbnail=None
) -> Reel:
    reel = Reel.objects.create(
        owner=owner,
        description=description,
        video=video,
        sound=sound,
        thumbnail=thumbnail,
    )
    link_hashtags_to_content(reel)
    return reel


def update_reel(reel: Reel, description: str) -> Reel:
    if description:
        unlink_hashtags_from_content(reel)
        reel.description = description
        link_hashtags_to_content(reel)

    reel.save()
    return reel


def delete_reel(reel: Reel) -> None:
    unlink_hashtags_from_content(reel)
    reel.delete()
