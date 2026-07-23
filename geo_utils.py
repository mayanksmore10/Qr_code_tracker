import requests
import traceback
from time import monotonic, sleep

BIGDATA_URL = "https://api.bigdatacloud.net/data/reverse-geocode-client"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

GEOCODE_CACHE = {}
_LAST_NOMINATIM_REQUEST_AT = 0.0
NOMINATIM_MIN_INTERVAL_SECONDS = 1.0


def _cache_key(latitude: float, longitude: float):
    return (round(latitude, 5), round(longitude, 5))


def _nominatim_fallback(latitude: float, longitude: float):
    global _LAST_NOMINATIM_REQUEST_AT

    cache_key = _cache_key(latitude, longitude)
    if cache_key in GEOCODE_CACHE:
        print(f"[GEO] Using cached reverse geocode for {cache_key}")
        return GEOCODE_CACHE[cache_key]

    now = monotonic()
    elapsed = now - _LAST_NOMINATIM_REQUEST_AT
    if elapsed < NOMINATIM_MIN_INTERVAL_SECONDS:
        sleep(NOMINATIM_MIN_INTERVAL_SECONDS - elapsed)

    _LAST_NOMINATIM_REQUEST_AT = monotonic()

    resp = requests.get(
        NOMINATIM_URL,
        params={
            "format": "jsonv2",
            "lat": latitude,
            "lon": longitude,
            "zoom": 18,
            "addressdetails": 1,
        },
        headers={"User-Agent": "qr_tracker_app_v2"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    address = data.get("address", {})
    place = (
        address.get("city")
        or address.get("town")
        or address.get("municipality")
        or address.get("village")
        or address.get("state_district")
        or address.get("district")
        or address.get("county")
        or data.get("display_name")
    )
    suburb = (
        address.get("suburb")
        or address.get("neighbourhood")
        or address.get("quarter")
        or address.get("residential")
    )
    road = address.get("road") or address.get("pedestrian") or address.get("footway")
    pincode = address.get("postcode") or address.get("post code")

    result = place, suburb, road, pincode
    GEOCODE_CACHE[cache_key] = result
    return result


def reverse_geocode(latitude: float, longitude: float):
    """Reverse-geocode using BigDataCloud and fall back to Nominatim for postcode lookup."""
    cache_key = _cache_key(latitude, longitude)
    if cache_key in GEOCODE_CACHE:
        print(f"[GEO] Using cached reverse geocode for {cache_key}")
        return GEOCODE_CACHE[cache_key]

    try:
        print(f"[GEO] Reverse geocoding: lat={latitude}, lon={longitude}")

        resp = requests.get(
            BIGDATA_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "localityLanguage": "en",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        print(f"[GEO] BigDataCloud response keys: {list(data.keys())}")

        # Extract fields with fallbacks
        place = (
            data.get("city")
            or data.get("locality")
            or data.get("principalSubdivision")
        )
        suburb = (
            data.get("locality")
            if data.get("city")
            else None
        )
        road = None  # BigDataCloud free tier doesn't return road-level data
        pincode = data.get("postcode") or None

        print(f"[GEO] Resolved -> place={place}, suburb={suburb}, road={road}, pincode={pincode}")

        if not pincode:
            print("[GEO] BigDataCloud returned no postcode; trying Nominatim fallback")
            result = _nominatim_fallback(latitude, longitude)
            GEOCODE_CACHE[cache_key] = result
            return result

        result = place, suburb, road, pincode
        GEOCODE_CACHE[cache_key] = result
        return result

    except requests.exceptions.Timeout:
        print("[GEO] ERROR: BigDataCloud request timed out")
        return None, None, None, None
    except requests.exceptions.RequestException as e:
        print(f"[GEO] ERROR: BigDataCloud request error: {e}")
        return None, None, None, None
    except Exception as e:
        print(f"[GEO] ERROR: Unexpected error during reverse geocoding: {e}")
        traceback.print_exc()
        return None, None, None, None