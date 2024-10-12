from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError
from apps.account.models import User
from ..models import Connection


class ErrorMessages:
    connection_exist = "You are already connected"
    request_connection_exist = "you have already request to user"


def request_connection(
    requester: User, receiver: User
) -> tuple[bool, str | Connection]:

    accept = not receiver.is_private
    connection = Connection.objects.filter(requester=requester, receiver=receiver)
    reverse_connection = Connection.objects.filter(
        requester=receiver, receiver=requester
    )

    if connection.exists():
        if connection.get().is_accept:
            return False, ErrorMessages.connection_exist
        else:
            return False, ErrorMessages.request_connection_exist

    if reverse_connection.exists():
        obj_reverse_connection = reverse_connection.get()
        if obj_reverse_connection.is_accept:
            return False, ErrorMessages.connection_exist
        else:
            obj_reverse_connection.is_accept = True
            obj_reverse_connection.save()
            return True, obj_reverse_connection

    try:
        connection = Connection.objects.create(
            requester=requester,
            receiver=receiver,
            is_accept=accept,
        )

        return True, connection
    except ValidationError as e:
        return False, str(e)


def reject_connection(requester: User, receiver: User) -> bool:
    try:
        connection = Connection.objects.pending().get(
            requester=requester, receiver=receiver
        )
        connection.delete()

        return True
    except ObjectDoesNotExist:
        return False


def accept_connection(requester: User, receiver: User) -> bool:
    try:
        connection = Connection.objects.pending().get(
            requester=requester, receiver=receiver
        )
        connection.is_accept = True
        connection.save()

        return True
    except ObjectDoesNotExist:
        return False
