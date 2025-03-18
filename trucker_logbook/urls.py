from django.urls import path
from . import views

urlpatterns = [
    path("trips/", views.TripListCreateView.as_view(), name="trip-list-create"),
    path(
        "trips/<int:pk>/",
        views.TripRetrieveUpdateDestroyView.as_view(),
        name="trip-retrieve-update-destroy",
    ),
    path(
        "trips/<int:trip_id>/logs/",
        views.LogEntryListCreateView.as_view(),
        name="logentry-list-create",
    ),
    path(
        "logs/<int:pk>/",
        views.LogEntryRetrieveUpdateDestroyView.as_view(),
        name="logentry-retrieve-update-destroy",
    ),
    path(
        "trips/<int:trip_id>/generate_logs/", views.generate_logs, name="generate-logs"
    ),  # Custom endpoint
    path(
        "trips/<int:trip_id>/configurations/",
        views.ConfigurationListCreateView.as_view(),
        name="configuration-list-create",
    ),
    path(
        "configurations/<int:pk>/",
        views.ConfigurationRetrieveUpdateDestroyView.as_view(),
        name="configuration-retrieve-update-destroy",
    ),
    path(
        "trips/check_existing/", views.check_existing_trip, name="check-existing-trip"
    ),  # New endpoint
    path(
        "trips/<int:trip_id>/daily_summary/",
        views.DailySummaryListView.as_view(),
        name="daily-summary-list",
    ),  # New endpoint
    path(
        "daily_summary/<int:pk>/",
        views.DailySummaryDetailView.as_view(),
        name="daily-summary-detail",
    ),  # New endpoint
    path("get-osrm-route/", views.get_osrm_route, name="get_osrm_route"),
]
