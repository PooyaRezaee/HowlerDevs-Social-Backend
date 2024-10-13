from django.urls import path, include


urlpatterns = [
    path("account/", include(("apps.account.urls", "account"))),
    path("connection/", include(("apps.connect.urls", "connection"))),
]
