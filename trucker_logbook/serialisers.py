from rest_framework import serializers
from .models import Trip, LogEntry, DailySummary, Configuration


class LogEntrySerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()  # Override default timestamp field

    class Meta:
        model = LogEntry
        fields = [
            "id",
            "timestamp",
            "duty_status",
            "location",
            "remarks",
            "latitude",
            "longitude",
        ]  # List only required fields

    def get_timestamp(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d | %H:%M:%S")  # Adjust format as needed


class TripSerializer(serializers.ModelSerializer):
    log_entries = LogEntrySerializer(
        many=True, read_only=True
    )  # Embed related log entries

    class Meta:
        model = Trip
        fields = "__all__"  # Or specify individual fields if needed


class DailySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySummary
        fields = "__all__"
        read_only_fields = ("trip", "date")  # These fields are automatically generated


class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = "__all__"
