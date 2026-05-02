"""
geocoding.py
Converts user-entered addresses into latitude/longitude coordinates.

This module is used before route optimisation:
addresses -> coordinates -> distance matrix -> route order
"""

from time import sleep
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


class GeocodingError(Exception):
    """Custom error for geocoding failures."""
    pass


geolocator = Nominatim(user_agent="final_year_route_optimiser")


def geocode_address(address: str, location_id: int) -> dict:
    """
    Convert a single address into a coordinate dictionary.

    Args:
        address: User-entered address string.
        location_id: Numeric ID used by the route optimiser.

    Returns:
        Dictionary containing id, address, lat, and lng.
    """

    if not address or not address.strip():
        raise GeocodingError("Address cannot be empty.")

    try:
        location = geolocator.geocode(address, timeout=10)

        if location is None:
            raise GeocodingError(f"Could not geocode address: {address}")

        return {
            "id": location_id,
            "address": address,
            "lat": round(location.latitude, 6),
            "lng": round(location.longitude, 6),
        }

    except GeocoderTimedOut:
        raise GeocodingError(f"Geocoding timed out for address: {address}")

    except GeocoderServiceError as error:
        raise GeocodingError(f"Geocoding service error for '{address}': {error}")


def geocode_addresses(addresses: list[str]) -> list[dict]:
    """
    Convert multiple addresses into coordinate dictionaries.

    Args:
        addresses: List of user-entered addresses.

    Returns:
        List of coordinate dictionaries.
    """

    if len(addresses) < 2:
        raise GeocodingError("At least two addresses are required to build a route.")

    coordinates = []

    for index, address in enumerate(addresses):
        coordinate = geocode_address(address, index)
        coordinates.append(coordinate)

        # Be polite to free geocoding services.
        sleep(1)

    return coordinates