from django.db.utils import IntegrityError
from core.logger import logging
from ..models import User
from ..validators import validate_password


def create_user(username: str, password: str) -> User | None:
    validate_password(password)

    try:
        return User.objects.create_user(username=username, password=password)
    except IntegrityError:
        logging.info("User creation was repeating")
        return None