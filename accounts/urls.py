from django.urls import path

from .views import (
    register_view,
    login_view,
    refresh_token_view,
    logout_view,
)


urlpatterns = [
    path(
        "register/",
        register_view,
        name="register",
    ),
    path(
        "login/",
        login_view,
        name="login",
    ),
    path(
    "refresh/",
    refresh_token_view,
    name="refresh",
    ),
    path(
        "logout/",
        logout_view,
        name="logout",
    ),

]