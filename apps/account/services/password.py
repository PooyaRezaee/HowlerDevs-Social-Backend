from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.cache import cache
from ..enums import CacheKeyPrefix

User = get_user_model()


def send_password_reset_code(user):
    code = get_random_string(6, allowed_chars="0123456789")
    cache.set(CacheKeyPrefix.RESET_PASSWORD.key(user.username), code, 600)
    send_mail(
        "Password Reset Code",
        f"Your password reset code is: {code}",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
    return code


def verify_password_reset_code(username, code):
    entry = cache.get(CacheKeyPrefix.RESET_PASSWORD.key(username))
    if not entry:
        return False
    if entry != code:
        return False
    return True


def reset_user_password_with_code(email, code, new_password):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return False
    if not verify_password_reset_code(user.username, code):
        return False
    user.set_password(new_password)
    user.save(update_fields=["password"])
    cache.delete(CacheKeyPrefix.RESET_PASSWORD.key(user.username))
    return True


def change_user_password(user, old_password, new_password):
    if not user.check_password(old_password):
        return False
    user.set_password(new_password)
    user.save(update_fields=["password"])
    return True
