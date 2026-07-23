from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import traceback

geolocator = Nominatim(user_agent="qr_tracker_app_v2")


def reverse_geocode(latitude: float, longitude: float):

    try:
        print(f"[GEO] Reverse geocoding: lat={latitude}, lon={longitude}")

        location = geolocator.reverse(
            f"{latitude}, {longitude}",
            exactly_one=True,
            addressdetails=True,
            timeout=10
        )

        if location is None:
            print("[GEO] Nominatim returned None (no location found)")
            return None, None, None, None

        if "address" not in location.raw:
            print(f"[GEO] No 'address' key in response. Raw: {location.raw}")
            return None, None, None, None

        address = location.raw["address"]
        print(f"[GEO] Raw address fields: {address}")

        # Expanded fallbacks to cover Indian city/district naming
        place = (
            address.get("city")
            or address.get("town")
            or address.get("municipality")
            or address.get("village")
            or address.get("state_district")
            or address.get("district")
            or address.get("county")
        )
        suburb = (
            address.get("suburb")
            or address.get("neighbourhood")
            or address.get("quarter")
            or address.get("residential")
            or address.get("county")   # fallback for Indian peri-urban areas
        )
        road = address.get("road") or address.get("pedestrian") or address.get("footway")
        pincode = address.get("postcode")

        print(f"[GEO] Resolved -> place={place}, suburb={suburb}, road={road}, pincode={pincode}")

        return place, suburb, road, pincode

    except GeocoderTimedOut:
        print("[GEO] ERROR: Nominatim request timed out")
        return None, None, None, None
    except GeocoderServiceError as e:
        print(f"[GEO] ERROR: Nominatim service error: {e}")
        return None, None, None, None
    except Exception as e:
        print(f"[GEO] ERROR: Unexpected error during reverse geocoding: {e}")
        traceback.print_exc()
        return None, None, None, None