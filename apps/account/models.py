import re
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from core import simple_send_mail, logger


class UserManager(BaseUserManager):
    def create_user(self, username: str, password: str, **extra_fields):
        if not username:
            raise ValueError("You should enter Username")

        if not password:
            raise ValueError("You should enter Password")
        
        user = self.model(username=username, **extra_fields)

        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, password: str, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_admin", True)
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, password, **extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[username_validator],
        error_messages={
            "unique": "A user with that username already exists.",
        },
        unique=True,
    )
    full_name = models.CharField(max_length=64,null=True)
    bio = models.CharField(max_length=512,null=True,blank=True)
    is_private = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField("date joined", auto_now_add=True)
    picture = models.ImageField("Image Profile",upload_to="img/profile",null=True,blank=True)


    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    USERNAME_FIELD = "username"

    def __str__(self):
        return self.username
    
    @property
    def is_staff(self):
        return self.is_admin