import os
import requests
import traceback

from dotenv import load_dotenv

load_dotenv()

OPENCAGE_URL = "https://api.opencagedata.com/geocode/v1/json"
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY", "")

GEOCODE_CACHE = {}


def _cache_key(latitude: float, longitude: float):
    return (round(latitude, 5), round(longitude, 5))


def reverse_geocode(latitude: float, longitude: float):
    """Reverse-geocode coordinates using the OpenCage API."""
    cache_key = _cache_key(latitude, longitude)
    if cache_key in GEOCODE_CACHE:
        print(f"[GEO] Using cached reverse geocode for {cache_key}")
        return GEOCODE_CACHE[cache_key]

    try:
        print(f"[GEO] Reverse geocoding: lat={latitude}, lon={longitude}")

        resp = requests.get(
            OPENCAGE_URL,
            params={
                "q": f"{latitude},{longitude}",
                "key": OPENCAGE_API_KEY,
                "language": "en",
                "no_annotations": 1,
                "limit": 1,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        if not results:
            print("[GEO] OpenCage returned no results")
            return None, None, None, None

        components = results[0].get("components", {})
        print(f"[GEO] OpenCage components: {components}")

        # Extract place (city / town / village / state_district)
        place = (
            components.get("city")
            or components.get("town")
            or components.get("municipality")
            or components.get("village")
            or components.get("state_district")
            or components.get("district")
            or components.get("county")
            or components.get("state")
        )

        # Extract suburb / neighbourhood
        suburb = (
            components.get("suburb")
            or components.get("neighbourhood")
            or components.get("quarter")
            or components.get("residential")
        )

        # Extract road
        road = (
            components.get("road")
            or components.get("pedestrian")
            or components.get("footway")
            or components.get("street")
        )

        # Extract pincode
        pincode = components.get("postcode")

        print(f"[GEO] Resolved -> place={place}, suburb={suburb}, road={road}, pincode={pincode}")

        result = place, suburb, road, pincode
        GEOCODE_CACHE[cache_key] = result
        return result

    except requests.exceptions.Timeout:
        print("[GEO] ERROR: OpenCage request timed out")
        return None, None, None, None
    except requests.exceptions.RequestException as e:
        print(f"[GEO] ERROR: OpenCage request error: {e}")
        return None, None, None, None
    except Exception as e:
        print(f"[GEO] ERROR: Unexpected error during reverse geocoding: {e}")
        traceback.print_exc()
        return None, None, None, None