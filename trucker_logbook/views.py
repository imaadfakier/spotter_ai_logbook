from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import (
    Trip,
    LogEntry,
    DailySummary,
    Configuration,
)
from .serialisers import (
    TripSerializer,
    LogEntrySerializer,
    DailySummarySerializer,
    ConfigurationSerializer,
)
from django.shortcuts import get_object_or_404
from datetime import timedelta
from .helper import generate_dummy_logs, delete_all_data

delete_all_data()

# Create your views here.


class TripListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list all trips or create a new trip.
    """

    queryset = Trip.objects.all()
    serializer_class = TripSerializer


class TripRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a specific trip.
    """

    queryset = Trip.objects.all()
    serializer_class = TripSerializer


class LogEntryListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list all log entries for a trip or create a new log entry.
    """

    serializer_class = LogEntrySerializer

    def get_queryset(self):
        trip_id = self.kwargs.get("trip_id")
        return LogEntry.objects.filter(trip_id=trip_id).order_by("timestamp")

    def perform_create(self, serializer):
        trip_id = self.kwargs.get("trip_id")
        trip = get_object_or_404(Trip, id=trip_id)
        serializer.save(trip=trip)


class LogEntryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a specific log entry.
    """

    queryset = LogEntry.objects.all()
    serializer_class = LogEntrySerializer


class DailySummaryListView(generics.ListAPIView):
    serializer_class = DailySummarySerializer

    def get_queryset(self):
        trip_id = self.kwargs.get("trip_id")
        return DailySummary.objects.filter(trip_id=trip_id)


class DailySummaryDetailView(generics.RetrieveAPIView):
    serializer_class = DailySummarySerializer
    queryset = DailySummary.objects.all()


@api_view(["POST"])
def check_existing_trip(request):
    """
    API endpoint to check if a trip with the given details already exists.
    """
    start_location = request.data.get("start_location")
    pickup_location = request.data.get("pickup_location")
    dropoff_location = request.data.get("dropoff_location")
    start_date = request.data.get("start_date")

    if not all([start_location, pickup_location, dropoff_location, start_date]):
        return Response(
            {"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        trip = Trip.objects.filter(
            start_location=start_location,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            start_date=start_date,
        ).first()

        if trip:
            # Serialize the trip, load all the daily logs, as well as all the trip data
            serializer = TripSerializer(trip)
            daily_summary = DailySummary.objects.filter(trip=trip).first()
            if daily_summary:
                daily_summary_serializer = DailySummarySerializer(daily_summary)
                return Response(
                    {
                        "exists": True,
                        "trip": serializer.data,
                        "daily_summary": daily_summary_serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"exists": True, "trip": serializer.data}, status=status.HTTP_200_OK
                )
        else:
            return Response({"exists": False}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Custom Log Generation Endpoint
@api_view(["POST"])
def generate_logs(request, trip_id):
    """
    API endpoint to generate daily logs for a given trip.
    This is where the core logic for simulating the driver's journey resides.
    """
    trip = get_object_or_404(Trip, id=trip_id)
    # Clear any existing logs.
    LogEntry.objects.filter(trip=trip).delete()

    # 1. Get trip details from the Trip object.
    start_location = trip.start_location
    pickup_location = trip.pickup_location
    dropoff_location = trip.dropoff_location
    start_date = trip.start_date

    # 2.  Get Configuration Values
    configuration = Configuration.objects.filter(trip=trip).first()
    if not configuration:
        configuration = Configuration.objects.create(trip=trip)

    # Generate our logs, using the helper function
    log_entries = generate_dummy_logs(
        trip, start_date, start_location, pickup_location, dropoff_location
    )

    LogEntry.objects.bulk_create(log_entries)

    # 4. Calculate and Save daily summary
    calculate_daily_summary(trip)
    return Response(
        {"status": "Logs generated successfully"}, status=status.HTTP_201_CREATED
    )


def calculate_daily_summary(trip):
    """
    Calculates and saves the daily summary information for a trip.
    """
    log_entries = trip.log_entries.all().order_by("timestamp")
    if not log_entries:
        return

    # Group log entries by date
    daily_logs = {}
    for entry in log_entries:
        date = entry.timestamp.date()
        if date not in daily_logs:
            daily_logs[date] = []
        daily_logs[date].append(entry)

    # Iterate through each day
    for date, entries in daily_logs.items():
        # Initialize values
        total_miles_driving = 0
        total_off_duty_hours = 0
        total_sleeper_berth_hours = 0
        total_driving_hours = 0
        total_on_duty_hours = 0

        # Get previous day's summary to increment total miles driving
        previous_day = date - timedelta(days=1)
        previous_summary = DailySummary.objects.filter(
            trip=trip, date=previous_day
        ).first()
        if previous_summary:
            total_miles_driving = previous_summary.total_miles_driving

        # Iterate through each log entry to get totals.
        for i in range(len(entries)):
            entry = entries[i]
            if i > 0:
                previous_entry = entries[i - 1]
                time_diff = entry.timestamp - previous_entry.timestamp
                hours = time_diff.total_seconds() / 3600

                if previous_entry.duty_status == "OD":
                    total_off_duty_hours += hours
                elif previous_entry.duty_status == "SB":
                    total_sleeper_berth_hours += hours
                elif previous_entry.duty_status == "DR":
                    total_driving_hours += hours
                    # TODO: This requires us to get the miles from the MAP API.
                    total_miles_driving += (
                        100  # Dummy value until we have that API working
                    )
                elif previous_entry.duty_status == "ON":
                    total_on_duty_hours += hours

        # Create or update the daily summary object
        DailySummary.objects.update_or_create(
            trip=trip,
            date=date,
            defaults={
                "total_miles_driving": total_miles_driving,
                "total_off_duty_hours": total_off_duty_hours,
                "total_sleeper_berth_hours": total_sleeper_berth_hours,
                "total_driving_hours": total_driving_hours,
                "total_on_duty_hours": total_on_duty_hours,
                "total_lines_3_4": total_driving_hours + total_on_duty_hours,
            },
        )


class ConfigurationListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list configurations or create a new configuration.
    """

    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer

    def get_queryset(self):
        trip_id = self.kwargs.get("trip_id")
        return Configuration.objects.filter(trip_id=trip_id)

    def perform_create(self, serializer):
        trip_id = self.kwargs.get("trip_id")
        trip = get_object_or_404(Trip, id=trip_id)
        serializer.save(trip=trip)


class ConfigurationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a specific configuration.
    """

    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
