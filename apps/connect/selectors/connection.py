from apps.account.models import User
from django.db.models import Q
from ..models import Connection


def list_connection_user_received_request(user: User) -> list[User]:
    return Connection.objects.received_requests(user)


def list_connection_user_sent_request(user: User) -> list[User]:
    return Connection.objects.sent_requests(user)


def list_connections(user: User) -> list[User]:
    connections = Connection.objects.accepted_with(user)
    return [
        conn.receiver if conn.requester == user else conn.requester
        for conn in connections
    ]


def user_connected_to(user1: User, user2: User) -> bool:
    return Connection.objects.between(user1, user2, is_accept=True).exists()


def count_connections(user: User) -> int:
    return Connection.objects.accepted_with(user).count()
