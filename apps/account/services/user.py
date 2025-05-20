from django.db.utils import IntegrityError
from django.contrib.auth.validators import UnicodeUsernameValidator
from core.logger import logging
from ..models import User
from ..validators import validate_password

username_validator = UnicodeUsernameValidator()


def create_user(username: str, password: str) -> User | None:
    username_validator(username)
    validate_password(password)

    try:
        return User.objects.create_user(username=username, password=password)
    except IntegrityError:
        logging.info("User creation was repeating")
        return None
