from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

geolocator = Nominatim(user_agent="qr_tracker_app")


def reverse_geocode(latitude: float, longitude: float):
    """
    Takes lat/lng, returns (place, suburb, road, pincode).
    Returns all None values if geocoding fails, instead of raising -
    so the caller never has to worry about this crashing the request.
    """
    try:
        location = geolocator.reverse(
            f"{latitude}, {longitude}",
            exactly_one=True,
            addressdetails=True,
            timeout=10
        )

        if location is None or "address" not in location.raw:
            return None, None, None, None

        address = location.raw["address"]

        place = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("county")
        )
        suburb = address.get("suburb") or address.get("neighbourhood")
        road = address.get("road")
        pincode = address.get("postcode")

        return place, suburb, road, pincode

    except (GeocoderTimedOut, GeocoderServiceError, Exception):
        # Nominatim down, rate-limited, or bad response - fail safe, don't crash
        return None, None, None, None