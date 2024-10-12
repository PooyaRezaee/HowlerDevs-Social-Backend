from apps.account.models import User
from django.test import TestCase
from ...services.connection import (
    accept_connection,
    reject_connection,
    request_connection,
    ErrorMessages,
)
from ...models import Connection


class ConnectionServicesTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="user1")
        self.user2 = User.objects.create(username="user2", is_private=False)
        self.user3 = User.objects.create(username="user3", is_private=True)
        self.user4 = User.objects.create(username="user4", is_private=True)

    def test_success_request_connection(self):
        status, connection = request_connection(self.user1, self.user2)
        self.assertTrue(status)
        self.assertIsInstance(connection, Connection)
        self.assertEqual(connection.requester, self.user1)
        self.assertEqual(connection.receiver, self.user2)
        self.assertTrue(connection.is_accept)

    def test_repeated_request_connection(self):
        request_connection(self.user1, self.user3)
        status, err_msg = request_connection(self.user1, self.user3)
        self.assertFalse(status)
        self.assertEqual(ErrorMessages.request_connection_exist, err_msg)

    def test_success_reject_connection(self):
        request_connection(self.user1, self.user3)
        status = reject_connection(self.user1, self.user3)
        self.assertTrue(status)
        self.assertFalse(
            Connection.objects.filter(
                requester=self.user1, receiver=self.user3
            ).exists()
        )

    def test_reject_connection_dont_exist(self):
        success = reject_connection(self.user1, self.user2)
        self.assertFalse(success)

    def test_reject_connection_accepted_before(self):
        status, connection = request_connection(self.user1, self.user3)
        accept_connection(self.user1, self.user3)

        status, err_msg = request_connection(self.user1, self.user3)
        self.assertFalse(status)
        self.assertEqual(ErrorMessages.connection_exist, err_msg)

    def test_success_accept_connection(self):
        request_connection(self.user1, self.user3)
        status = accept_connection(self.user1, self.user3)
        self.assertTrue(status)
        connection = Connection.objects.get(requester=self.user1, receiver=self.user3)
        self.assertTrue(connection.is_accept)
        self.assertEqual(Connection.objects.pending().count(), 0)
        self.assertEqual(Connection.objects.accepted().count(), 1)

    def test_accept_connection_dont_exist(self):
        status = accept_connection(self.user1, self.user2)
        self.assertFalse(status)

    def test_accept_connection_accepted_before(self):
        request_connection(self.user1, self.user3)
        accept_connection(self.user1, self.user3)
        status = accept_connection(self.user1, self.user3)
        self.assertFalse(status)

    def test_request_connection_for_public_account(self):
        status, connection = request_connection(self.user1, self.user2)
        self.assertTrue(status)
        self.assertTrue(connection.is_accept)
        self.assertEqual(Connection.objects.pending().count(), 0)
        self.assertEqual(Connection.objects.accepted().count(), 1)

    def test_prevent_reverse_connection(self):
        _status, connection = request_connection(self.user1, self.user2)
        status, err_msg = request_connection(self.user2, self.user1)

        self.assertFalse(status)
        self.assertEqual(ErrorMessages.connection_exist, err_msg)

    def test_request_connection_and_automatic_accept_after_reverse_request(self):
        status_1, connection = request_connection(self.user1, self.user3)
        status_2, connection = request_connection(self.user4, self.user3)

        self.assertFalse(connection.is_accept)
        self.assertFalse(connection.is_accept)
        self.assertEqual(Connection.objects.pending().count(), 2)

        status_reverse_1, connection = request_connection(self.user3, self.user1)
        status_reverse_2, connection = request_connection(self.user3, self.user4)

        self.assertEqual(Connection.objects.pending().count(), 0)
        self.assertTrue(connection.is_accept)
        self.assertTrue(connection.is_accept)
        self.assertEqual(Connection.objects.accepted().count(), 2)

        self.assertTrue(status_1)
        self.assertTrue(status_2)
        self.assertTrue(status_reverse_1)
        self.assertTrue(status_reverse_2)
