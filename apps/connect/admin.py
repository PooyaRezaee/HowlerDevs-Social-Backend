from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Connection


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ("id", "requester_link", "receiver_link", "is_accept", "created_at")
    list_filter = ("is_accept", "created_at")
    search_fields = (
        "requester__username",
        "receiver__username",
    )
    list_editable = ("is_accept",)
    ordering = ("-created_at",)

    def requester_link(self, obj):
        url = reverse("admin:account_user_change", args=[obj.requester.pk])
        return format_html('<a href="{}">{}</a>', url, obj.requester.username)

    requester_link.short_description = "Requester"
    requester_link.admin_order_field = "requester__username"

    def receiver_link(self, obj):
        url = reverse("admin:account_user_change", args=[obj.receiver.pk])
        return format_html('<a href="{}">{}</a>', url, obj.receiver.username)

    receiver_link.short_description = "Receiver"
    receiver_link.admin_order_field = "receiver__username"
