from ..models import Hashtag, Post, Reel


def get_hashtag_by_name(name: str) -> Hashtag | None:
    return Hashtag.objects.filter(name=name).first()


def get_posts_by_hashtag(hashtag_name: str) -> Post | None:
    hashtag = get_hashtag_by_name(hashtag_name)
    if hashtag:
        return hashtag.posts.all()
    return None


def get_reels_by_hashtag(hashtag_name: str) -> Reel | None:
    hashtag = get_hashtag_by_name(hashtag_name)
    if hashtag:
        return hashtag.reels.all()
    return None


def get_content_by_hashtag(hashtag_name: str) -> dict[str, Post | Reel] | None:
    hashtag = get_hashtag_by_name(hashtag_name)
    if hashtag:
        posts = hashtag.posts.all()
        reels = hashtag.reels.all()
        return {"posts": posts, "reels": reels}
    return None
