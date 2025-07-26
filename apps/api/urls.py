from django.urls import path, include


urlpatterns = [
    path("account/", include(("apps.account.urls", "account"))),
    path("connection/", include(("apps.connect.urls", "connection"))),
    path("content/", include(("apps.content.urls", "content"))),
    path("comment/", include(("apps.comment.urls", "comment"))),
]
