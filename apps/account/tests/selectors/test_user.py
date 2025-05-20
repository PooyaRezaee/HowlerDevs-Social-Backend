from unittest.mock import patch
from django.test import TestCase
from ...selectors.user import count_users
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSelectorTests(TestCase):

    def setUp(self):
        User.objects.create_user(username="user1User", password="TestPassword123")
        User.objects.create_user(username="user2User", password="TestPassword123")
        User.objects.create_user(username="user3User", password="TestPassword123")

    def test_count_users(self):
        expected_count = 3

        self.assertEqual(count_users(), expected_count)
