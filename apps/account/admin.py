from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        ("Global", {"fields": ("username", "full_name")}),
        (
            "Personal",
            {
                "classes": ("tabular",),
                "fields": ("bio", "picture", "is_private"),
            },
        ),
        (
            "Permissions",
            {"fields": ("is_active", "is_admin", "is_superuser", "user_permissions")},
        ),
        (
            "Event Times",
            {"classes": ("tabular",), "fields": ("last_login", "joined_at")},
        ),
    )

    add_fieldsets = (
        (
            "Personal",
            {
                "classes": ("wide",),
                "fields": ("username", "full_name", "is_private", "is_admin"),
            },
        ),
        (
            "Security",
            {
                "classes": ("wide",),
                "fields": ("password1", "password2"),
            },
        ),
        ("Special Access", {"classes": ("wide",), "fields": ("is_admin",)}),
    )

    readonly_fields = ("joined_at", "last_login", "password", "is_superuser")

    ordering = ("username", "joined_at")
    filter_horizontal = ("groups", "user_permissions")
    list_display = (
        "username",
        "full_name",
        "last_login",
        "is_active",
        "is_private",
        "is_admin",
        "joined_at",
    )
    search_fields = ("username", "full_name")
    list_filter = ("is_active", "is_private", "is_admin", "joined_at")
    actions = ["disable_account", "enable_account"]

    @admin.action(description="Disable users")
    def disable_account(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Enable users")
    def enable_account(self, request, queryset):
        queryset.update(is_active=True)
