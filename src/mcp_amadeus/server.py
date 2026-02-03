"""MCP Server for Amadeus Travel API.

Provides tools for:
- Flight search, booking, and management
- Hotel search, booking, and ratings
- Airport/city information and analytics
- Travel recommendations and predictions
- Tours and activities
- Ground transfers

Backward-compatible wrapper that delegates to the operations layer.
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .client import AmadeusClient
from .operations import flights, hotels, airports, activities, transfers, analytics, orders, misc

# Initialize MCP server
mcp = FastMCP("amadeus")

# Lazy singleton
_client: AmadeusClient | None = None


def _get_client() -> AmadeusClient:
    global _client
    if _client is None:
        _client = AmadeusClient()
    return _client


def _json(obj: object) -> str:
    return json.dumps(obj, indent=2, default=str)


# ============== FLIGHT TOOLS ==============


@mcp.tool()
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    adults: int = 1,
    travel_class: str = "ECONOMY",
    nonstop: bool = False,
    max_results: int = 10,
) -> str:
    """Search for flight offers.

    Args:
        origin: Origin airport IATA code (e.g., 'JFK')
        destination: Destination airport IATA code (e.g., 'LAX')
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date for round trip (YYYY-MM-DD)
        adults: Number of adult passengers
        travel_class: ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST
        nonstop: Only show nonstop flights
        max_results: Maximum number of offers to return
    """
    return _json(flights.search_flights(
        _get_client(), origin, destination, departure_date,
        return_date, adults, travel_class, nonstop, max_results,
    ))


@mcp.tool()
def get_flight_price(offer_id: str, flight_offer: str) -> str:
    """Confirm price for a flight offer.

    Args:
        offer_id: Flight offer ID from search results
        flight_offer: Full flight offer JSON from search results
    """
    return _json(flights.get_flight_price(_get_client(), json.loads(flight_offer)))


@mcp.tool()
def search_flight_inspiration(
    origin: str,
    max_price: Optional[int] = None,
    departure_date: Optional[str] = None,
) -> str:
    """Get flight destination inspiration based on cheapest flights.

    Args:
        origin: Origin airport IATA code
        max_price: Maximum price in USD
        departure_date: Departure date or date range
    """
    return _json(flights.search_flight_inspiration(
        _get_client(), origin, max_price, departure_date,
    ))


@mcp.tool()
def search_flight_availability(
    origin: str,
    destination: str,
    departure_date: str,
    adults: int = 1,
) -> str:
    """Search for available seats on flights.

    Args:
        origin: Origin airport IATA code
        destination: Destination airport IATA code
        departure_date: Departure date (YYYY-MM-DD)
        adults: Number of adult passengers
    """
    return _json(flights.search_flight_availability(
        _get_client(), origin, destination, departure_date, adults,
    ))


@mcp.tool()
def get_branded_fares(flight_offer: str) -> str:
    """Get branded fare upsell options for a flight offer.

    Args:
        flight_offer: JSON string of a single flight offer
    """
    return _json(flights.get_branded_fares(_get_client(), json.loads(flight_offer)))


@mcp.tool()
def get_seatmap(flight_offer: str) -> str:
    """Get seatmap for a flight offer showing available seats.

    Args:
        flight_offer: JSON string of a single flight offer
    """
    return _json(flights.get_seatmap(_get_client(), json.loads(flight_offer)))


@mcp.tool()
def get_flight_status(
    carrier_code: str,
    flight_number: str,
    departure_date: str,
) -> str:
    """Get real-time flight status information.

    Args:
        carrier_code: IATA airline code (e.g., 'BA', 'AA')
        flight_number: Flight number (e.g., '326')
        departure_date: Scheduled departure date (YYYY-MM-DD)
    """
    return _json(flights.get_flight_status(
        _get_client(), carrier_code, flight_number, departure_date,
    ))


# ============== HOTEL TOOLS ==============


@mcp.tool()
def search_hotels(
    city_code: str,
    check_in: str,
    check_out: str,
    adults: int = 1,
    rooms: int = 1,
    radius: int = 5,
    max_results: int = 10,
) -> str:
    """Search for hotels in a city.

    Args:
        city_code: City IATA code (e.g., 'NYC')
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        adults: Number of adults
        rooms: Number of rooms
        radius: Search radius in km from city center
        max_results: Maximum hotels to return
    """
    return _json(hotels.search_hotels(
        _get_client(), city_code, check_in, check_out, adults, rooms, radius, max_results,
    ))


@mcp.tool()
def get_hotel_details(hotel_id: str) -> str:
    """Get detailed information about a specific hotel.

    Args:
        hotel_id: Hotel ID from search results
    """
    return _json(hotels.get_hotel_details(_get_client(), hotel_id))


@mcp.tool()
def search_hotel_by_name(keyword: str, max_results: int = 20) -> str:
    """Search for hotels by name (autocomplete).

    Args:
        keyword: Hotel name or partial name
        max_results: Maximum number of results
    """
    return _json(hotels.search_hotel_by_name(_get_client(), keyword, max_results))


@mcp.tool()
def get_hotel_ratings(hotel_ids: str) -> str:
    """Get sentiment analysis ratings for hotels.

    Args:
        hotel_ids: Comma-separated list of Amadeus hotel IDs
    """
    return _json(hotels.get_hotel_ratings(_get_client(), hotel_ids))


@mcp.tool()
def book_hotel(offer_id: str, guests: str, payment: str) -> str:
    """Book a hotel room.

    Args:
        offer_id: Hotel offer ID
        guests: JSON string of guest details
        payment: JSON string with payment details
    """
    return _json(hotels.book_hotel(
        _get_client(), offer_id, json.loads(guests), json.loads(payment),
    ))


# ============== LOCATION TOOLS ==============


@mcp.tool()
def search_airports(keyword: str) -> str:
    """Search for airports by city name or airport code.

    Args:
        keyword: City name or airport code
    """
    return _json(airports.search_airports(_get_client(), keyword))


@mcp.tool()
def search_cities(keyword: str) -> str:
    """Search for cities by name.

    Args:
        keyword: City name
    """
    return _json(airports.search_cities(_get_client(), keyword))


@mcp.tool()
def get_airport_routes(airport_code: str) -> str:
    """Get direct flight routes from an airport.

    Args:
        airport_code: Airport IATA code
    """
    return _json(airports.get_airport_routes(_get_client(), airport_code))


@mcp.tool()
def get_nearest_airports(
    latitude: float,
    longitude: float,
    radius: int = 100,
    max_results: int = 10,
) -> str:
    """Find nearest airports to a geographical location.

    Args:
        latitude: Latitude
        longitude: Longitude
        radius: Search radius in km (max 500)
        max_results: Maximum airports to return
    """
    return _json(airports.get_nearest_airports(
        _get_client(), latitude, longitude, radius, max_results,
    ))


@mcp.tool()
def get_airline_destinations(airline_code: str, max_results: int = 50) -> str:
    """Get all destinations served by a specific airline.

    Args:
        airline_code: IATA airline code
        max_results: Maximum destinations
    """
    return _json(airports.get_airline_destinations(_get_client(), airline_code, max_results))


@mcp.tool()
def get_airport_on_time_performance(airport_code: str, date: str) -> str:
    """Predict on-time performance for flights from an airport.

    Args:
        airport_code: IATA airport code
        date: Date to check (YYYY-MM-DD)
    """
    return _json(airports.get_airport_on_time_performance(_get_client(), airport_code, date))


# ============== TRAVEL INSIGHTS ==============


@mcp.tool()
def get_travel_recommendations(city_code: str, category: str = "SIGHTS") -> str:
    """Get travel recommendations for a city.

    Args:
        city_code: City IATA code
        category: SIGHTS, NIGHTLIFE, RESTAURANT, SHOPPING
    """
    return _json(misc.get_travel_recommendations(_get_client(), city_code, category))


@mcp.tool()
def get_recommended_destinations(
    origin_cities: str,
    traveler_interest: str = "ADVENTURE",
) -> str:
    """Get destination recommendations based on traveler interests.

    Args:
        origin_cities: Comma-separated IATA city codes
        traveler_interest: Interest category
    """
    return _json(misc.get_recommended_destinations(
        _get_client(), origin_cities, traveler_interest,
    ))


# ============== FLIGHT ANALYTICS ==============


@mcp.tool()
def get_busiest_travel_period(
    city_code: str,
    year: str,
    direction: str = "ARRIVING",
) -> str:
    """Get the busiest travel periods for a city.

    Args:
        city_code: IATA city code
        year: Year (YYYY)
        direction: ARRIVING or DEPARTING
    """
    return _json(analytics.get_busiest_travel_period(
        _get_client(), city_code, year, direction,
    ))


@mcp.tool()
def get_most_booked_destinations(
    origin_city: str,
    year: str,
    max_results: int = 20,
) -> str:
    """Get most booked flight destinations from a city.

    Args:
        origin_city: IATA city code
        year: Year (YYYY)
        max_results: Maximum destinations
    """
    return _json(analytics.get_most_booked_destinations(
        _get_client(), origin_city, year, max_results,
    ))


@mcp.tool()
def get_most_traveled_destinations(
    origin_city: str,
    year: str,
    max_results: int = 20,
) -> str:
    """Get most traveled flight destinations from a city.

    Args:
        origin_city: IATA city code
        year: Year (YYYY)
        max_results: Maximum destinations
    """
    return _json(analytics.get_most_traveled_destinations(
        _get_client(), origin_city, year, max_results,
    ))


@mcp.tool()
def analyze_flight_price(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
) -> str:
    """Analyze if a flight price is good compared to historical data.

    Args:
        origin: Origin airport IATA code
        destination: Destination airport IATA code
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD)
    """
    return _json(analytics.analyze_flight_price(
        _get_client(), origin, destination, departure_date, return_date,
    ))


# ============== FLIGHT PREDICTIONS ==============


@mcp.tool()
def predict_flight_delay(
    origin: str,
    destination: str,
    departure_date: str,
    departure_time: str,
    arrival_date: str,
    arrival_time: str,
    carrier_code: str,
    flight_number: str,
    aircraft_code: str,
    duration: str,
) -> str:
    """Predict the probability of flight delay.

    Args:
        origin: Origin airport IATA code
        destination: Destination airport IATA code
        departure_date: Departure date (YYYY-MM-DD)
        departure_time: Departure time (HH:MM:SS)
        arrival_date: Arrival date (YYYY-MM-DD)
        arrival_time: Arrival time (HH:MM:SS)
        carrier_code: IATA airline code
        flight_number: Flight number
        aircraft_code: ICAO aircraft code
        duration: Duration in ISO 8601 (e.g., 'PT3H30M')
    """
    return _json(analytics.predict_flight_delay(
        _get_client(), origin, destination, departure_date, departure_time,
        arrival_date, arrival_time, carrier_code, flight_number, aircraft_code, duration,
    ))


@mcp.tool()
def predict_flight_choice(flight_offers: str) -> str:
    """Predict which flight offer travelers are most likely to choose.

    Args:
        flight_offers: JSON string of flight offers
    """
    return _json(analytics.predict_flight_choice(_get_client(), json.loads(flight_offers)))


@mcp.tool()
def predict_trip_purpose(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str,
    search_date: Optional[str] = None,
) -> str:
    """Predict if a trip is for business or leisure.

    Args:
        origin: Origin airport IATA code
        destination: Destination airport IATA code
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD)
        search_date: Date of search (YYYY-MM-DD)
    """
    return _json(analytics.predict_trip_purpose(
        _get_client(), origin, destination, departure_date, return_date, search_date,
    ))


# ============== FLIGHT BOOKING ==============


@mcp.tool()
def create_flight_order(
    flight_offer: str,
    travelers: str,
    contact_email: str,
    contact_phone: str,
) -> str:
    """Create a flight booking order.

    Args:
        flight_offer: JSON string of flight offer
        travelers: JSON string of traveler details
        contact_email: Contact email
        contact_phone: Contact phone with country code
    """
    return _json(orders.create_flight_order(
        _get_client(), json.loads(flight_offer), json.loads(travelers),
        contact_email, contact_phone,
    ))


@mcp.tool()
def get_flight_order(order_id: str) -> str:
    """Retrieve details of an existing flight order.

    Args:
        order_id: Flight order ID
    """
    return _json(orders.get_flight_order(_get_client(), order_id))


@mcp.tool()
def cancel_flight_order(order_id: str) -> str:
    """Cancel an existing flight order.

    Args:
        order_id: Flight order ID to cancel
    """
    return _json(orders.cancel_flight_order(_get_client(), order_id))


# ============== TOURS AND ACTIVITIES ==============


@mcp.tool()
def search_activities(latitude: float, longitude: float, radius: int = 5) -> str:
    """Search for tours and activities near a location.

    Args:
        latitude: Latitude
        longitude: Longitude
        radius: Search radius in km
    """
    return _json(activities.search_activities(_get_client(), latitude, longitude, radius))


@mcp.tool()
def get_activity_details(activity_id: str) -> str:
    """Get detailed information about a specific activity.

    Args:
        activity_id: Activity ID
    """
    return _json(activities.get_activity_details(_get_client(), activity_id))


# ============== TRANSFERS ==============


@mcp.tool()
def search_transfers(
    start_latitude: float,
    start_longitude: float,
    end_latitude: float,
    end_longitude: float,
    transfer_date: str,
    transfer_time: str,
    passengers: int = 1,
) -> str:
    """Search for ground transfer options between two locations.

    Args:
        start_latitude: Pickup latitude
        start_longitude: Pickup longitude
        end_latitude: Dropoff latitude
        end_longitude: Dropoff longitude
        transfer_date: Date (YYYY-MM-DD)
        transfer_time: Time (HH:MM)
        passengers: Number of passengers
    """
    return _json(transfers.search_transfers(
        _get_client(), start_latitude, start_longitude,
        end_latitude, end_longitude, transfer_date, transfer_time, passengers,
    ))


@mcp.tool()
def book_transfer(
    offer_id: str,
    passengers: str,
    contact_email: str,
    contact_phone: str,
) -> str:
    """Book a ground transfer.

    Args:
        offer_id: Transfer offer ID
        passengers: JSON string of passengers
        contact_email: Contact email
        contact_phone: Contact phone
    """
    return _json(transfers.book_transfer(
        _get_client(), offer_id, json.loads(passengers), contact_email, contact_phone,
    ))


@mcp.tool()
def get_transfer_order(order_id: str) -> str:
    """Get details of a transfer booking.

    Args:
        order_id: Transfer order ID
    """
    return _json(transfers.get_transfer_order(_get_client(), order_id))


@mcp.tool()
def cancel_transfer(order_id: str) -> str:
    """Cancel a transfer booking.

    Args:
        order_id: Transfer order ID to cancel
    """
    return _json(transfers.cancel_transfer(_get_client(), order_id))


# ============== TRIP PARSER ==============


@mcp.tool()
def parse_trip_document(document_content: str, document_type: str = "HTML") -> str:
    """Parse a booking confirmation to extract structured trip data.

    Args:
        document_content: Base64-encoded document content
        document_type: HTML, EML, or PDF
    """
    return _json(misc.parse_trip_document(_get_client(), document_content, document_type))


@mcp.tool()
def get_parsed_trip(document_id: str) -> str:
    """Get the parsed trip data from a previously submitted document.

    Args:
        document_id: Document ID from parse_trip_document
    """
    return _json(misc.get_parsed_trip(_get_client(), document_id))


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
