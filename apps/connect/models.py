from django.db import models
from django.db.models import Q

class ConnectionManager(models.Manager):
    def pending(self):
        return self.filter(is_accept=False)

    def accepted(self):
        return self.filter(is_accept=True)
    
    def between(self, user1, user2, is_accept=None):
        qs = self.filter(
            Q(requester=user1, receiver=user2) |
            Q(requester=user2, receiver=user1)
        )
        if is_accept is not None:
            qs = qs.filter(is_accept=is_accept)
        return qs

    def sent_requests(self, user):
        return self.pending().filter(requester=user).select_related("receiver")

    def received_requests(self, user):
        return self.pending().filter(receiver=user).select_related("requester")

    def accepted_with(self, user):
        return self.accepted().filter(
            Q(requester=user) | Q(receiver=user)
        ).select_related("requester", "receiver")


class Connection(models.Model):
    requester = models.ForeignKey(
        "account.User", on_delete=models.CASCADE, related_name="connect_request"
    )
    receiver = models.ForeignKey(
        "account.User", on_delete=models.CASCADE, related_name="connect_recive"
    )
    is_accept = models.BooleanField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.requester} To {self.receiver} | {self.is_accept}"

    objects = ConnectionManager()

    class Meta:
        verbose_name = "Connection"
        verbose_name_plural = "Connections"
        unique_together = ["requester", "receiver"]
        indexes = [
            models.Index(fields=["requester", "receiver"]),
            models.Index(fields=["receiver", "requester"]),
        ]
