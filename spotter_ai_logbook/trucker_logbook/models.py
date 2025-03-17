from django.db import models

# Create your models here.


class Trip(models.Model):
    """
    Represents an entire trip.
    """

    start_location = models.CharField(
        max_length=255
    )  # Free-form text (e.g., "123 Main St, Anytown, USA")
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    current_cycle_hours = models.FloatField(default=0)  # Driver's current cycle hours
    start_date = models.DateField()  # Date the trip began
    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Timestamp of when the trip was created

    def __str__(self):
        return f"Trip from {self.start_location} to {self.dropoff_location} on {self.start_date}"


class LogEntry(models.Model):
    """
    Represents a single entry in the driver's log. Each entry corresponds
    to a change in duty status.
    """

    trip = models.ForeignKey(Trip, related_name="log_entries", on_delete=models.CASCADE)
    timestamp = models.DateTimeField()  # Date and time of the duty status change
    duty_status = models.CharField(
        max_length=2,
        choices=[
            ("OD", "Off Duty"),
            ("SB", "Sleeper Berth"),
            ("DR", "Driving"),
            ("ON", "On Duty (Not Driving)"),
        ],
    )
    location = models.CharField(max_length=255)  # City, State
    remarks = models.TextField(blank=True, null=True)  # Description of activity
    latitude = models.FloatField(blank=True, null=True)  # Optional: For map integration
    longitude = models.FloatField(
        blank=True, null=True
    )  # Optional: For map integration

    def __str__(self):
        formatted_timestamp = self.timestamp.strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # Format timestamp
        return f"{formatted_timestamp} | {self.duty_status} | {self.location}"


class DailySummary(models.Model):
    """
    Stores the daily summary information for the log sheet recap section.
    This is automatically calculated from the LogEntry objects.
    """

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    date = models.DateField()  # Date the summary is for
    total_miles_driving = models.FloatField(default=0)
    total_off_duty_hours = models.FloatField(default=0)
    total_sleeper_berth_hours = models.FloatField(default=0)
    total_driving_hours = models.FloatField(default=0)
    total_on_duty_hours = models.FloatField(default=0)
    total_lines_3_4 = models.FloatField(
        default=0
    )  # Sum of driving and on duty not driving

    def __str__(self):
        return f"Daily Summary for {self.date}"


class Configuration(models.Model):
    """
    Configuration settings for the log generation.  This allows us to tweak the
    algorithm without changing the code.
    """

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    fuel_stop_frequency = models.FloatField(default=1000)  # Miles between fuel stops
    pickup_dropoff_time = models.FloatField(default=1)  # Hours for pickup and dropoff
    minimum_rest_stop = models.FloatField(
        default=0.5
    )  # Minimum rest stop duration in hours
