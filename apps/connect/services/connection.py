from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.account.models import User
from ..models import Connection


class ErrorMessages:
    connection_exist = "You are already connected"
    request_connection_exist = "you have already request to user"
    cannot_connect_to_self = "you can't connect to yourself"


def request_connection(
    requester: User, receiver: User
) -> tuple[bool, str | Connection]:
    """Request a connection between two users."""
    
    if requester.pk == receiver.pk:
        return False, ErrorMessages.cannot_connect_to_self

    existing = Connection.objects.filter(
        requester=requester, receiver=receiver
    ).first()

    if existing:
        if existing.is_accept:
            return False, ErrorMessages.connection_exist
        return False, ErrorMessages.request_connection_exist

    reverse = Connection.objects.filter(
        requester=receiver, receiver=requester
    ).first()

    if reverse:
        if reverse.is_accept:
            return False, ErrorMessages.connection_exist
        reverse.is_accept = True
        reverse.save()
        return True, reverse

    try:
        connection = Connection.objects.create(
            requester=requester,
            receiver=receiver,
            is_accept=not receiver.is_private,
        )
        return True, connection
    except ValidationError as e:
        return False, str(e)


def reject_connection(requester: User, receiver: User) -> bool:
    """Reject a connection request."""
    connection = Connection.objects.pending().filter(
        requester=requester, receiver=receiver
    ).first()
    if not connection:
        return False
    connection.delete()
    return True


def accept_connection(requester: User, receiver: User) -> bool:
    """Accept a connection request."""
    connection = Connection.objects.pending().filter(
        requester=requester, receiver=receiver
    ).first()
    if not connection:
        return False
    connection.is_accept = True
    connection.save()
    return True


def remove_connection(requester: User, receiver: User) -> bool:
    """Remove any connection between two users (accepted or not)."""
    try:
        connection = Connection.objects.between(requester, receiver).first()
        if connection:
            connection.delete()
            return True
        return False
    except IntegrityError:
        return False
