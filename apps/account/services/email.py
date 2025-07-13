from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.cache import cache
from core import logger

from ..enums import CacheKeyPrefix

User = get_user_model()


def send_email_change_request(user, new_email):
    code = get_random_string(6, allowed_chars="0123456789")
    cache.set(CacheKeyPrefix.RESET_EMAIL.key(user.pk), f"{code}-{new_email}", 600)
    send_mail(
        "Email Change Request",
        f"Hello {user.username},This is your code for change your email in social django to this address : {code}",
        settings.DEFAULT_FROM_EMAIL,
        [new_email],
    )


def confirm_email_change(user, code):
    code_and_email = cache.get(CacheKeyPrefix.RESET_EMAIL.key(user.pk))
    if code_and_email is None:
        return False
    try:
        main_code, new_email = code_and_email.split("-")
    except ValueError:
        logger.error(
            f"Can't split code and email from redis key value is : {code_and_email}"
        )
        return False

    if int(main_code) != int(code):
        return False

    cache.delete(CacheKeyPrefix.RESET_EMAIL.key(user.pk))
    user.email = new_email
    user.save(update_fields=["email"])
    return True
