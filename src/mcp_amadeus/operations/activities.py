"""Tours and activities operations."""

from __future__ import annotations

from ..client import AmadeusClient


def search_activities(
    client: AmadeusClient,
    latitude: float,
    longitude: float,
    radius: int = 5,
) -> list[dict]:
    """Search for tours and activities near a location."""
    params = {"latitude": latitude, "longitude": longitude, "radius": radius}
    data = client.request("GET", "/v1/shopping/activities", params=params)

    result = []
    for activity in data.get("data", [])[:20]:
        result.append({
            "id": activity.get("id"),
            "name": activity.get("name"),
            "description": activity.get("shortDescription"),
            "rating": activity.get("rating"),
            "booking_link": activity.get("bookingLink"),
            "price": activity.get("price"),
            "pictures": activity.get("pictures", [])[:3],
        })
    return result


def get_activity_details(client: AmadeusClient, activity_id: str) -> dict:
    """Get detailed information about a specific activity."""
    data = client.request("GET", f"/v1/shopping/activities/{activity_id}")
    activity = data.get("data", {})
    return {
        "id": activity.get("id"),
        "name": activity.get("name"),
        "description": activity.get("description"),
        "rating": activity.get("rating"),
        "reviews_count": activity.get("reviewsCount"),
        "booking_link": activity.get("bookingLink"),
        "price": activity.get("price"),
        "duration": activity.get("duration"),
        "categories": activity.get("categories"),
        "pictures": activity.get("pictures"),
    }
