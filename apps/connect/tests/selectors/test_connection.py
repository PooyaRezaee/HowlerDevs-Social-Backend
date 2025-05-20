from apps.account.models import User
from django.test import TestCase
from ...selectors.connection import (
    list_connections,
    list_connection_user_sent_request,
    list_connection_user_received_request,
)
from ...models import Connection


class ConnectionServicesTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="user1")
        self.user2 = User.objects.create(username="user2")
        self.user3 = User.objects.create(username="user3")
        self.user4 = User.objects.create(username="user4")

        self.con1 = Connection.objects.create(
            requester=self.user1, receiver=self.user2, is_accept=True
        )
        self.con2 = Connection.objects.create(
            requester=self.user2, receiver=self.user3, is_accept=True
        )

        self.con3 = Connection.objects.create(
            requester=self.user3, receiver=self.user4, is_accept=True
        )

        self.con4 = Connection.objects.create(
            requester=self.user1, receiver=self.user4, is_accept=False
        )
        self.con5 = Connection.objects.create(
            requester=self.user2, receiver=self.user4, is_accept=False
        )

    def test_get_list_connection_users(self):
        con_user1 = list_connections(self.user1)
        con_user2 = list_connections(self.user2)
        con_user3 = list_connections(self.user3)
        con_user4 = list_connections(self.user4)

        self.assertEqual(len(con_user1), 1)
        self.assertEqual(len(con_user2), 2)
        self.assertEqual(len(con_user3), 2)
        self.assertEqual(len(con_user4), 1)
        # Need more test

    def test_get_list_connection_user_sent(self):
        con_user1 = list_connection_user_sent_request(self.user1)
        con_user2 = list_connection_user_sent_request(self.user2)
        con_user3 = list_connection_user_sent_request(self.user3)
        con_user4 = list_connection_user_sent_request(self.user4)

        self.assertEqual(con_user1.count(), 1)
        self.assertEqual(con_user2.count(), 1)
        self.assertEqual(con_user3.count(), 0)
        self.assertEqual(con_user4.count(), 0)

    def test_get_list_connection_user_received(self):
        con_user1 = list_connection_user_received_request(self.user1)
        con_user2 = list_connection_user_received_request(self.user2)
        con_user3 = list_connection_user_received_request(self.user3)
        con_user4 = list_connection_user_received_request(self.user4)

        self.assertEqual(con_user1.count(), 0)
        self.assertEqual(con_user2.count(), 0)
        self.assertEqual(con_user3.count(), 0)
        self.assertEqual(con_user4.count(), 2)
