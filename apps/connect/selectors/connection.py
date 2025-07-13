from apps.account.models import User
from django.db.models import Q
from ..models import Connection


def list_connection_user_received_request(user: User) -> list[User]:
    """List of connection obj that have been sent to the user and user can be accept or reject"""
    return (
        Connection.objects.pending().filter(receiver=user).select_related("requester")
    )


def list_connection_user_sent_request(user: User) -> list[User]:
    """List of connection obj sent by the user and waiting for the user's approval"""
    return (
        Connection.objects.pending().filter(requester=user).select_related("receiver")
    )


def list_connections(user: User) -> list[User]:
    """List of all users connected to the user"""
    connections = (
        Connection.objects.accepted()
        .filter(Q(requester=user) | Q(receiver=user))
        .select_related("receiver", "requester")
    )
    users = [
        connection.receiver if connection.requester == user else connection.requester
        for connection in connections
    ]
    return users


def user_connected_to(user1: User, user2: User) -> bool:
    return Connection.objects.filter(
        Q(requester=user1, receiver=user2) | Q(requester=user2, receiver=user1),
        is_accept=True,
    ).exists()


def count_connections(user: User) -> int:
    return (
        Connection.objects.accepted()
        .filter(Q(requester=user) | Q(receiver=user))
        .count()
    )
