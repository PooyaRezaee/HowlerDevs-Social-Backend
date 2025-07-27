from django import forms
from django.utils.html import format_html
from django.contrib import messages
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        ("Main Info", {"fields": ("username", "full_name", "email", "picture", "picture_tag")}),
        ("Personal Info", {"fields": ("bio", "is_private")}),
        ("Permissions", {"fields": ("is_active", "is_admin", "is_superuser", "is_2fa_enabled", "totp_secret")}),
        ("Password", {"fields": ("password_with_link",)}),
        ("Times", {"fields": ("last_login", "joined_at")}),
    )
    add_fieldsets = (
        ("Main Info", {"fields": ("username", "full_name", "email", "is_private", "is_admin", "picture")}),
        ("Security", {"fields": ("password1", "password2")}),
    )
    readonly_fields = ("joined_at", "last_login", "password", "is_superuser", "picture_tag", "totp_secret", "password_with_link")
    ordering = ("username", "joined_at")
    filter_horizontal = ("groups", "user_permissions")
    list_display = (
        "username",
        "full_name",
        "email",
        "profile_image",
        "is_active",
        "is_admin",
        "is_2fa_enabled",
    )
    search_fields = ("username", "full_name", "email")
    list_filter = ("is_active", "is_admin", "is_2fa_enabled")
    actions = ["disable_account", "enable_account"]

    def profile_image(self, obj):
        if obj.picture:
            return format_html('<img src="{}" width="40" height="40" style="border-radius:50%;object-fit:cover;" />', obj.picture.url)
        return "-"
    profile_image.short_description = "Profile Image"
    profile_image.allow_tags = True

    def picture_tag(self, obj):
        if obj.picture:
            return format_html('<img src="{}" width="80" height="80" style="border-radius:50%;object-fit:cover;" />', obj.picture.url)
        return "-"
    picture_tag.short_description = "Profile Preview"
    picture_tag.allow_tags = True

    def is_2fa_enabled(self, obj):
        return obj.is_2fa_enabled
    is_2fa_enabled.boolean = True
    is_2fa_enabled.short_description = "2FA Enabled?"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        user = self.get_object(request, object_id)
        if user:
            url = reverse('admin:auth_user_password_change', args=[user.pk])
            extra_context['password_change_link'] = mark_safe(f'<a class="button" href="{url}">Change password</a>')
            extra_context['password_change_help'] = "The 'Change password' button appears above this form. Clicking it will take you to the Django built-in password change page for this user."
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def password_with_link(self, obj):
        if not obj:
            return ""
        url = reverse('admin:auth_user_password_change', args=[obj.pk])
        return mark_safe(f'<span style="font-family:monospace">{obj.password}</span> <a class="button" href="{url}">Change password</a>')
    password_with_link.short_description = "Password (hashed)"
