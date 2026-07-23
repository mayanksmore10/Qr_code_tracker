import requests
import traceback

BIGDATA_URL = "https://api.bigdatacloud.net/data/reverse-geocode-client"


def reverse_geocode(latitude: float, longitude: float):
    """Reverse-geocode using BigDataCloud (free, no API key required)."""

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

        return place, suburb, road, pincode

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