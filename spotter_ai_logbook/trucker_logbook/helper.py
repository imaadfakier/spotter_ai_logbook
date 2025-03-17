import requests
from datetime import timedelta
import random
from django.utils import timezone
from .models import Trip, DailySummary, LogEntry, Configuration

# List of possible city-state combinations (expand this list!)
CITIES = [
    "Atlanta, GA",
    "Chicago, IL",
    "Houston, TX",
    "Phoenix, AZ",
    "Philadelphia, PA",
    "San Antonio, TX",
    "San Diego, CA",
    "Dallas, TX",
    "San Jose, CA",
    "Austin, TX",
    "Jacksonville, FL",
    "Fort Worth, TX",
    "Columbus, OH",
    "Charlotte, NC",
    "San Francisco, CA",
    "Indianapolis, IN",
    "Seattle, WA",
    "Denver, CO",
    "Washington, DC",
    "Boston, MA",
    # Add more
]


def geocode_location(location_string):
    """
    Geocodes a location string using Nominatim.
    """
    try:
        headers = {
            "User-Agent": "TruckerLogbookApp/1.0"
        }  # Replace with your app name/version
        url = f"https://nominatim.openstreetmap.org/search?q={location_string}&format=json&limit=1"
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if data:
            latitude = float(data[0]["lat"])
            longitude = float(data[0]["lon"])
            return latitude, longitude
        else:
            return None  # No results found for that location
    except requests.exceptions.RequestException as e:
        return None  # Handle request errors (e.g., connection errors, timeouts)
    except (KeyError, ValueError) as e:
        return None  # Handle errors related to unexpected response format


def generate_dummy_logs(
    trip, start_date, start_location, pickup_location, dropoff_location
):
    """
    Generates a complex set of dummy log entries for a multi-day trip.
    """

    log_entries = []
    current_time = timezone.make_aware(
        timezone.datetime.combine(start_date, timezone.datetime.min.time())
    )  # Start of the day
    current_location = start_location
    total_driving_hours = 0
    total_on_duty_hours = 0
    day_count = 0

    # Helper lambda to add a random amount of minutes to current_time
    add_random_minutes = lambda hours: timedelta(
        minutes=random.randint(0, int(hours * 60))
    )

    # Helper function to get lat/lon for a location
    def get_lat_lon(location):
        coords = geocode_location(location)
        if coords:
            return coords[0], coords[1]
        else:
            return None, None

    start_lat, start_lon = get_lat_lon(start_location)
    pickup_lat, pickup_lon = get_lat_lon(pickup_location)
    dropoff_lat, dropoff_lon = get_lat_lon(dropoff_location)

    def generate_intermediate_location():
        """Generates a random intermediate location from the CITIES list, not equal to current locations"""
        intermediate_location = random.choice(CITIES)
        while intermediate_location in [
            current_location,
            start_location,
            pickup_location,
            dropoff_location,
        ]:
            intermediate_location = random.choice(CITIES)
        return intermediate_location

    while (
        current_location != dropoff_location and day_count < 5
    ):  # Simulate a 5-day trip at most
        day_count += 1
        # Start of Day
        log_entries.append(
            LogEntry(
                trip=trip,
                timestamp=current_time,
                duty_status="OD",
                location=current_location,
                remarks="Start of day",
                latitude=start_lat,
                longitude=start_lon,
            )
        )
        current_time += add_random_minutes(1)  # Add up to 60 mins to the function
        log_entries.append(
            LogEntry(
                trip=trip,
                timestamp=current_time,
                duty_status="ON",
                location=current_location,
                remarks="Pre-trip inspection",
                latitude=start_lat,
                longitude=start_lon,
            )
        )
        current_time += add_random_minutes(0.5)

        # Driving for the first half of the day
        driving_hours1 = random.uniform(3, 4)  # 3-4 hours driving
        log_entries.append(
            LogEntry(
                trip=trip,
                timestamp=current_time,
                duty_status="DR",
                location="En Route",
                remarks="Driving",
                latitude=start_lat,
                longitude=start_lon,
            )
        )
        current_time += timedelta(hours=driving_hours1)
        total_driving_hours += driving_hours1
        total_on_duty_hours += driving_hours1

        # Break and Fuel Stop
        intermediate_location = generate_intermediate_location()  # New Location
        intermediate_lat, intermediate_lon = get_lat_lon(
            intermediate_location
        )  # Geocode the location
        log_entries.append(
            LogEntry(
                trip=trip,
                timestamp=current_time,
                duty_status="ON",
                location=intermediate_location,
                remarks="Fuel stop and 30-minute break",
                latitude=intermediate_lat,
                longitude=intermediate_lon,
            )
        )
        current_time += timedelta(minutes=30)

        # Driving for the second half of the day
        driving_hours2 = random.uniform(3, 4)
        log_entries.append(
            LogEntry(
                trip=trip,
                timestamp=current_time,
                duty_status="DR",
                location="En Route",
                remarks="Driving",
                latitude=intermediate_lat,
                longitude=intermediate_lon,
            )
        )
        current_time += timedelta(hours=driving_hours2)
        total_driving_hours += driving_hours2
        total_on_duty_hours += driving_hours2

        # Check to see if we need a break
        if total_driving_hours > 8:
            log_entries.append(
                LogEntry(
                    trip=trip,
                    timestamp=current_time,
                    duty_status="ON",
                    location=intermediate_location,
                    remarks="30-minute break",
                    latitude=intermediate_lat,
                    longitude=intermediate_lon,
                )
            )
            current_time += timedelta(minutes=30)
            total_driving_hours = 0

        # Sleeper Berth
        sleeper_berth_location = generate_intermediate_location()  # New Location
        sleeper_berth_lat, sleeper_berth_lon = get_lat_lon(
            sleeper_berth_location
        )  # Geocode
        log_entries.append(
            LogEntry(
                trip=trip,
                timestamp=current_time,
                duty_status="SB",
                location=sleeper_berth_location,
                remarks="Sleeper berth break",
                latitude=sleeper_berth_lat,
                longitude=sleeper_berth_lon,
            )
        )
        current_time += timedelta(hours=8)

        # Driving for the third half of the day
        driving_hours3 = random.uniform(2, 3)
        log_entries.append(
            LogEntry(
                trip=trip,
                timestamp=current_time,
                duty_status="DR",
                location="En Route",
                remarks="Driving",
                latitude=sleeper_berth_lat,
                longitude=sleeper_berth_lon,
            )
        )
        current_time += timedelta(hours=driving_hours3)
        total_driving_hours += driving_hours3
        total_on_duty_hours += driving_hours3

        # Check to see if we need a break
        if total_driving_hours > 8:
            log_entries.append(
                LogEntry(
                    trip=trip,
                    timestamp=current_time,
                    duty_status="ON",
                    location=intermediate_location,
                    remarks="30-minute break",
                    latitude=intermediate_lat,
                    longitude=intermediate_lon,
                )
            )
            current_time += timedelta(minutes=30)
            total_driving_hours = 0

        # On-Duty not driving (Pick Up)
        on_duty_hours = random.uniform(0.5, 1)
        log_entries.append(
            LogEntry(
                trip=trip,
                timestamp=current_time,
                duty_status="ON",
                location=pickup_location,
                remarks="Loading/Unloading Freight",
                latitude=pickup_lat,
                longitude=pickup_lon,
            )
        )
        current_time += timedelta(hours=on_duty_hours)

        # End of Day
        end_of_day_location = generate_intermediate_location()  # New Location
        end_of_day_lat, end_of_day_lon = get_lat_lon(end_of_day_location)  # Geocode
        log_entries.append(
            LogEntry(
                trip=trip,
                timestamp=current_time,
                duty_status="OD",
                location=end_of_day_location,
                remarks="End of day",
                latitude=end_of_day_lat,
                longitude=end_of_day_lon,
            )
        )
        current_time = timezone.make_aware(
            timezone.datetime.combine(
                current_time.date() + timedelta(days=1), timezone.datetime.min.time()
            )
        )  # Start of the day
        current_location = end_of_day_location
        total_driving_hours = 0
        total_on_duty_hours = 0

    # Delivery Location
    log_entries.append(
        LogEntry(
            trip=trip,
            timestamp=current_time,
            duty_status="ON",
            location=dropoff_location,
            remarks="Dropoff",
            latitude=dropoff_lat,
            longitude=dropoff_lon,
        )
    )
    return log_entries


def delete_all_data():
    # Delete it.
    Trip.objects.all().delete()
    LogEntry.objects.all().delete()
    DailySummary.objects.all().delete()
    Configuration.objects.all().delete()
