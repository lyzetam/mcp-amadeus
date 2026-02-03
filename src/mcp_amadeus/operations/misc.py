"""Miscellaneous operations: recommendations, trip parser."""

from __future__ import annotations

from ..client import AmadeusClient


def get_travel_recommendations(
    client: AmadeusClient,
    city_code: str,
    category: str = "SIGHTS",
) -> list[dict]:
    """Get travel recommendations for a city."""
    params = {"cityCode": city_code.upper(), "category": category}
    try:
        data = client.request("GET", "/v1/reference-data/locations/pois", params=params)
    except Exception as e:
        return [{"message": f"Recommendations not available: {str(e)}"}]

    result = []
    for poi in data.get("data", [])[:15]:
        result.append({
            "name": poi.get("name"),
            "category": poi.get("category"),
            "tags": poi.get("tags", []),
            "rank": poi.get("rank"),
            "location": poi.get("geoCode"),
        })
    return result


def get_recommended_destinations(
    client: AmadeusClient,
    origin_cities: str,
    traveler_interest: str = "ADVENTURE",
) -> dict:
    """Get destination recommendations based on traveler interests."""
    params = {"cityCodes": origin_cities.upper(), "travelerCountryCode": "US"}
    data = client.request(
        "GET", "/v1/reference-data/recommended-locations", params=params
    )

    destinations = []
    for dest in data.get("data", [])[:15]:
        destinations.append({
            "destination": dest.get("name"),
            "iata_code": dest.get("iataCode"),
            "country": dest.get("address", {}).get("countryName"),
            "score": dest.get("score"),
            "type": dest.get("subType"),
            "location": dest.get("geoCode"),
        })
    return {"based_on": origin_cities, "recommendations": destinations}


def parse_trip_document(
    client: AmadeusClient,
    document_content: str,
    document_type: str = "HTML",
) -> dict:
    """Parse a booking confirmation to extract structured trip data."""
    request_body = {
        "data": {"type": "trip-parser-job", "content": document_content}
    }
    data = client.request(
        "POST", "/v3/travel/trip-parser/pnr-documents", json_data=request_body
    )
    result = data.get("data", {})
    return {
        "job_id": result.get("id"),
        "status": result.get("status"),
        "trips": result.get("trips", []),
    }


def get_parsed_trip(client: AmadeusClient, document_id: str) -> dict:
    """Get the parsed trip data from a previously submitted document."""
    data = client.request(
        "GET", f"/v3/travel/trip-parser/pnr-documents/{document_id}"
    )
    result = data.get("data", {})
    return {
        "document_id": result.get("id"),
        "status": result.get("status"),
        "trips": result.get("trips", []),
    }
