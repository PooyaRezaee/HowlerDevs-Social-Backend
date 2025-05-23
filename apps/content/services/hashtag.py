import re
from django.db.utils import DataError
from core import logger
from ..models import Hashtag, Content

HASHTAG_PATTERN = r"#(\w+)"


def extract_hashtags(description: str) -> list[str]:
    return re.findall(HASHTAG_PATTERN, description)


def link_hashtags_to_content(content_instance: Content):
    hashtags_in_description = extract_hashtags(content_instance.description)

    for hashtag_name in hashtags_in_description:
        try:
            hashtag, _ = Hashtag.objects.get_or_create(name=hashtag_name)
            hashtag.contents.add(content_instance)
        except DataError:
            logger.warning(f"Hashtag too long: {hashtag_name}")
            continue


def unlink_hashtags_from_content(content_instance: Content):
    hashtags_in_description = extract_hashtags(content_instance.description)
    for hashtag_name in hashtags_in_description:
        hashtag = Hashtag.objects.filter(name=hashtag_name).first()
        if not hashtag:
            logger.warning(f"Hashtag '{hashtag_name}' referenced but not found.")
            continue

        hashtag.contents.remove(content_instance)

        if not hashtag.contents.exists():
            hashtag.delete()
