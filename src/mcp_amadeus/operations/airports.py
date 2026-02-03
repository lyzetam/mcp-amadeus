"""Airport and city search operations."""

from __future__ import annotations

from ..client import AmadeusClient


def search_airports(client: AmadeusClient, keyword: str) -> list[dict]:
    """Search for airports by city name or airport code."""
    params = {"keyword": keyword, "subType": "AIRPORT"}
    data = client.request("GET", "/v1/reference-data/locations", params=params)

    result = []
    for loc in data.get("data", [])[:10]:
        result.append({
            "iata_code": loc.get("iataCode"),
            "name": loc.get("name"),
            "city": loc.get("address", {}).get("cityName"),
            "country": loc.get("address", {}).get("countryName"),
        })
    return result


def search_cities(client: AmadeusClient, keyword: str) -> list[dict]:
    """Search for cities by name."""
    params = {"keyword": keyword, "subType": "CITY"}
    data = client.request("GET", "/v1/reference-data/locations", params=params)

    result = []
    for loc in data.get("data", [])[:10]:
        result.append({
            "iata_code": loc.get("iataCode"),
            "name": loc.get("name"),
            "country": loc.get("address", {}).get("countryName"),
        })
    return result


def get_airport_routes(client: AmadeusClient, airport_code: str) -> list[dict]:
    """Get direct flight routes from an airport."""
    params = {"departureAirportCode": airport_code.upper()}
    data = client.request("GET", "/v1/airport/direct-destinations", params=params)

    result = []
    for dest in data.get("data", []):
        result.append({
            "destination": dest.get("destination"),
            "name": dest.get("name"),
        })
    return result


def get_nearest_airports(
    client: AmadeusClient,
    latitude: float,
    longitude: float,
    radius: int = 100,
    max_results: int = 10,
) -> list[dict]:
    """Find nearest airports to a geographical location."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "radius": min(radius, 500),
        "page[limit]": max_results,
        "sort": "relevance",
    }
    data = client.request("GET", "/v1/reference-data/locations/airports", params=params)

    result = []
    for airport in data.get("data", []):
        result.append({
            "iata_code": airport.get("iataCode"),
            "name": airport.get("name"),
            "city": airport.get("address", {}).get("cityName"),
            "country": airport.get("address", {}).get("countryName"),
            "distance_km": airport.get("distance", {}).get("value"),
            "location": airport.get("geoCode"),
        })
    return result


def get_airline_destinations(
    client: AmadeusClient,
    airline_code: str,
    max_results: int = 50,
) -> list[dict]:
    """Get all destinations served by a specific airline."""
    params = {"airlineCode": airline_code.upper(), "max": max_results}
    data = client.request("GET", "/v1/airline/destinations", params=params)

    result = []
    for dest in data.get("data", []):
        result.append({
            "city": dest.get("name"),
            "iata_code": dest.get("iataCode"),
            "type": dest.get("subtype"),
        })
    return result


def get_airport_on_time_performance(
    client: AmadeusClient,
    airport_code: str,
    date: str,
) -> dict:
    """Predict on-time performance for flights from an airport."""
    params = {"airportCode": airport_code.upper(), "date": date}
    data = client.request("GET", "/v1/airport/predictions/on-time", params=params)

    result = data.get("data", {})
    return {
        "airport": airport_code.upper(),
        "date": date,
        "on_time_probability": result.get("probability"),
        "result": result.get("result"),
    }
