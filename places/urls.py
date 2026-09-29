from django.urls import path
from .views import PlaceListCreateView, PlaceDetailView


urlpatterns = [
    path("places/", PlaceListCreateView.as_view(), name="places-list-create"),
    path("places/<int:place_id>/", PlaceDetailView.as_view(), name="place-detail"),
]