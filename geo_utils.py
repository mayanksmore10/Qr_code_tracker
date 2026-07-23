from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError, GeocoderRateLimited
import traceback
from time import monotonic, sleep

geolocator = Nominatim(user_agent="qr_tracker_app_v2")

GEOCODE_CACHE = {}
_LAST_NOMINATIM_REQUEST_AT = 0.0
NOMINATIM_MIN_INTERVAL_SECONDS = 1.0


def _cache_key(latitude: float, longitude: float):
    return (round(latitude, 5), round(longitude, 5))


def _reverse_geocode_with_throttle(latitude: float, longitude: float):
    global _LAST_NOMINATIM_REQUEST_AT

    now = monotonic()
    elapsed = now - _LAST_NOMINATIM_REQUEST_AT
    if elapsed < NOMINATIM_MIN_INTERVAL_SECONDS:
        sleep(NOMINATIM_MIN_INTERVAL_SECONDS - elapsed)

    _LAST_NOMINATIM_REQUEST_AT = monotonic()

    return geolocator.reverse(
        f"{latitude}, {longitude}",
        exactly_one=True,
        addressdetails=True,
        timeout=10
    )


def reverse_geocode(latitude: float, longitude: float):
    cache_key = _cache_key(latitude, longitude)
    if cache_key in GEOCODE_CACHE:
        print(f"[GEO] Using cached reverse geocode for {cache_key}")
        return GEOCODE_CACHE[cache_key]

    try:
        print(f"[GEO] Reverse geocoding: lat={latitude}, lon={longitude}")

        location = _reverse_geocode_with_throttle(latitude, longitude)

        if location is None:
            print("[GEO] Nominatim returned None (no location found)")
            result = None, None, None, None
            GEOCODE_CACHE[cache_key] = result
            return result

        if "address" not in location.raw:
            print(f"[GEO] No 'address' key in response. Raw: {location.raw}")
            result = None, None, None, None
            GEOCODE_CACHE[cache_key] = result
            return result

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

        result = place, suburb, road, pincode
        GEOCODE_CACHE[cache_key] = result
        return result

    except GeocoderRateLimited as e:
        print(f"[GEO] ERROR: Nominatim rate limited: {e}")
        result = None, None, None, None
        GEOCODE_CACHE[cache_key] = result
        return result
    except GeocoderTimedOut:
        print("[GEO] ERROR: Nominatim request timed out")
        result = None, None, None, None
        GEOCODE_CACHE[cache_key] = result
        return result
    except GeocoderServiceError as e:
        print(f"[GEO] ERROR: Nominatim service error: {e}")
        result = None, None, None, None
        GEOCODE_CACHE[cache_key] = result
        return result
    except Exception as e:
        print(f"[GEO] ERROR: Unexpected error during reverse geocoding: {e}")
        traceback.print_exc()
        result = None, None, None, None
        GEOCODE_CACHE[cache_key] = result
        return result