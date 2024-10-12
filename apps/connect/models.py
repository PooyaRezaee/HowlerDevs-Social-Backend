from django.db import models


class ConnectionManager(models.Manager):
    def pending(self):
        return self.filter(is_accept=False)

    def accepted(self):
        return self.filter(is_accept=True)


class Connection(models.Model):
    requester = models.ForeignKey(
        "account.User", on_delete=models.CASCADE, related_name="connect_request"
    )
    receiver = models.ForeignKey(
        "account.User", on_delete=models.CASCADE, related_name="connect_recive"
    )
    is_accept = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.requester} To {self.reciver} | {self.is_accept}"

    objects = ConnectionManager()

    class Meta:
        verbose_name = "Connection"
        verbose_name_plural = "Connections"
        unique_together = ["requester", "receiver"]
