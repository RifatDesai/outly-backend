from django.contrib import admin
from django.urls import include, path
from places.urls import urlpatterns as places_urlpatterns

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "api/v1/auth/",
        include("accounts.urls"),
    ),

    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),

    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
        name="swagger-ui",
    ),
    path(
    "api/v1/users/",
    include("profiles.urls"),
    ),
    path(
    "api/v1/",
    include("follows.urls"),
    ),
    path("api/v1/", include("posts.urls")),
    path("api/v1/", include("comments.urls")),
    path("api/v1/", include("activities.urls")),
    path("api/v1/", include(places_urlpatterns)),
    path("api/v1/", include("trails.urls")),
    path("api/v1/events/", include("events.urls")),
]