from apps.account.models import User
from django.core.exceptions import ValidationError
from ..models import Post, MediaContent, Content
from .hashtag import link_hashtags_to_content, unlink_hashtags_from_content


def create_post(owner: User, description: str, thumbnail=None) -> Post:
    post = Post.objects.create(
        owner=owner, description=description, thumbnail=thumbnail
    )
    link_hashtags_to_content(post)

    return post


def delete_post(post: Post) -> None:
    unlink_hashtags_from_content(post)
    post.delete()


def create_media_content(
    owner: User, description: str, file, media_type: str, thumbnail=None
) -> MediaContent:
    try:
        if media_type not in ["video", "audio"]:
            raise ValueError("Wrong Type")

        media_content = MediaContent.objects.create(
            owner=owner,
            description=description,
            file=file,
            media_type=media_type,
            thumbnail=thumbnail,
        )
        link_hashtags_to_content(media_content)
        return True, media_content
    except ValidationError as e:
        return False, e


def delete_media_content(media_content: MediaContent) -> None:
    unlink_hashtags_from_content(media_content)
    media_content.delete()


def update_content(content: Content, description: str = None) -> Content:
    if description:
        unlink_hashtags_from_content(content)
        content.description = description
        link_hashtags_to_content(content)
        content.save()

    return content
