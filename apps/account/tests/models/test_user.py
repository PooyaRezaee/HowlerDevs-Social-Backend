from django.test import TestCase
from django.contrib.auth import get_user_model
from model_bakery import baker
from unittest.mock import patch

User = get_user_model()


class UserModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make("account.User")

    def test_create_user_with_username_successful(self):
        username = "testUser"
        password = "TestPassword123"
        user = User.objects.create_user(username=username, password=password)

        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)

    def test_create_user_with_no_username_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(username="", password="TestPassword123")

    def test_create_user_with_no_password_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(username="testUser", password="")

    def test_create_superuser(self):
        username = "superuserUser"
        password = "SuperPassword123"
        user = User.objects.create_superuser(username=username, password=password)

        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_admin)

    def test_user_str_method(self):
        username = "testUser"
        user = User.objects.create_user(username=username, password="TestPassword123")
        self.assertEqual(str(user), username)
