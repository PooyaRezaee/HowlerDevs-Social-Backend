import re
from django.db.utils import DataError
from core import logger
from ..models import Hashtag, Post, Reel, BaseContent

HASHTAG_PATTERN = r"#(\w+)"


def extract_hashtags(description: str) -> list[str]:
    return re.findall(HASHTAG_PATTERN, description)


def link_hashtags_to_content(content_instance: BaseContent):
    hashtags_in_description = extract_hashtags(content_instance.description)

    for hashtag_name in hashtags_in_description:
        try:
            hashtag, created = Hashtag.objects.get_or_create(name=hashtag_name)

            if isinstance(content_instance, Post):
                hashtag.posts.add(content_instance)
            elif isinstance(content_instance, Reel):
                hashtag.reels.add(content_instance)
        except DataError:
            continue  # for if hashtag more than 64 character


def unlink_hashtags_from_content(content_instance: BaseContent):
    hashtags_in_description = extract_hashtags(content_instance.description)
    for hashtag_name in hashtags_in_description:
        if not Hashtag.objects.filter(name=hashtag_name).exists():
            logger.warning(f"Hashtag '{hashtag_name}' detected in description during update but missing from the hashtags table — possible inconsistency.")
            continue

        hashtag = Hashtag.objects.filter(name=hashtag_name).get()
        if hashtag:
            if isinstance(content_instance, Post):
                hashtag.posts.remove(content_instance)
            elif isinstance(content_instance, Reel):
                hashtag.reels.remove(content_instance)

        if not hashtag.posts.exists() and not hashtag.reels.exists():
            hashtag.delete()
