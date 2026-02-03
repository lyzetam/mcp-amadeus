"""LangChain tool wrappers for Amadeus Travel API operations."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Optional

from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field

from .client import AmadeusClient
from .operations import flights, hotels, airports, activities, transfers, analytics, orders, misc


@lru_cache
def _get_client() -> AmadeusClient:
    """Singleton AmadeusClient from environment variables."""
    return AmadeusClient()


def _json(obj: object) -> str:
    return json.dumps(obj, indent=2, default=str)


# ── Flight tools ─────────────────────────────────────────────────────


class SearchFlightsArgs(BaseModel):
    origin: str = Field(description="Origin airport IATA code (e.g., 'JFK')")
    destination: str = Field(description="Destination airport IATA code (e.g., 'LAX')")
    departure_date: str = Field(description="Departure date (YYYY-MM-DD)")
    return_date: Optional[str] = Field(default=None, description="Return date for round trip")
    adults: int = Field(default=1, description="Number of adult passengers")
    travel_class: str = Field(default="ECONOMY", description="ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST")
    nonstop: bool = Field(default=False, description="Only nonstop flights")
    max_results: int = Field(default=10, description="Maximum offers to return")


@tool(args_schema=SearchFlightsArgs)
def amadeus_search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    adults: int = 1,
    travel_class: str = "ECONOMY",
    nonstop: bool = False,
    max_results: int = 10,
) -> str:
    """Search for flight offers."""
    return _json(flights.search_flights(
        _get_client(), origin, destination, departure_date,
        return_date, adults, travel_class, nonstop, max_results,
    ))


class FlightOfferArgs(BaseModel):
    flight_offer: str = Field(description="Full flight offer JSON from search results")


@tool(args_schema=FlightOfferArgs)
def amadeus_get_flight_price(flight_offer: str) -> str:
    """Confirm price for a flight offer."""
    return _json(flights.get_flight_price(_get_client(), json.loads(flight_offer)))


class FlightInspirationArgs(BaseModel):
    origin: str = Field(description="Origin airport IATA code")
    max_price: Optional[int] = Field(default=None, description="Maximum price in USD")
    departure_date: Optional[str] = Field(default=None, description="Departure date or range")


@tool(args_schema=FlightInspirationArgs)
def amadeus_search_flight_inspiration(
    origin: str,
    max_price: Optional[int] = None,
    departure_date: Optional[str] = None,
) -> str:
    """Get flight destination inspiration based on cheapest flights."""
    return _json(flights.search_flight_inspiration(
        _get_client(), origin, max_price, departure_date,
    ))


class FlightAvailabilityArgs(BaseModel):
    origin: str = Field(description="Origin airport IATA code")
    destination: str = Field(description="Destination airport IATA code")
    departure_date: str = Field(description="Departure date (YYYY-MM-DD)")
    adults: int = Field(default=1, description="Number of adult passengers")


@tool(args_schema=FlightAvailabilityArgs)
def amadeus_search_flight_availability(
    origin: str,
    destination: str,
    departure_date: str,
    adults: int = 1,
) -> str:
    """Search for available seats on flights."""
    return _json(flights.search_flight_availability(
        _get_client(), origin, destination, departure_date, adults,
    ))


@tool(args_schema=FlightOfferArgs)
def amadeus_get_branded_fares(flight_offer: str) -> str:
    """Get branded fare upsell options for a flight offer."""
    return _json(flights.get_branded_fares(_get_client(), json.loads(flight_offer)))


@tool(args_schema=FlightOfferArgs)
def amadeus_get_seatmap(flight_offer: str) -> str:
    """Get seatmap for a flight offer showing available seats."""
    return _json(flights.get_seatmap(_get_client(), json.loads(flight_offer)))


class FlightStatusArgs(BaseModel):
    carrier_code: str = Field(description="IATA airline code (e.g., 'BA', 'AA')")
    flight_number: str = Field(description="Flight number (e.g., '326')")
    departure_date: str = Field(description="Scheduled departure date (YYYY-MM-DD)")


@tool(args_schema=FlightStatusArgs)
def amadeus_get_flight_status(
    carrier_code: str,
    flight_number: str,
    departure_date: str,
) -> str:
    """Get real-time flight status information."""
    return _json(flights.get_flight_status(
        _get_client(), carrier_code, flight_number, departure_date,
    ))


# ── Hotel tools ──────────────────────────────────────────────────────


class SearchHotelsArgs(BaseModel):
    city_code: str = Field(description="City IATA code (e.g., 'NYC')")
    check_in: str = Field(description="Check-in date (YYYY-MM-DD)")
    check_out: str = Field(description="Check-out date (YYYY-MM-DD)")
    adults: int = Field(default=1, description="Number of adults")
    rooms: int = Field(default=1, description="Number of rooms")
    radius: int = Field(default=5, description="Search radius in km")
    max_results: int = Field(default=10, description="Maximum hotels to return")


@tool(args_schema=SearchHotelsArgs)
def amadeus_search_hotels(
    city_code: str,
    check_in: str,
    check_out: str,
    adults: int = 1,
    rooms: int = 1,
    radius: int = 5,
    max_results: int = 10,
) -> str:
    """Search for hotels in a city."""
    return _json(hotels.search_hotels(
        _get_client(), city_code, check_in, check_out, adults, rooms, radius, max_results,
    ))


class HotelIdArgs(BaseModel):
    hotel_id: str = Field(description="Hotel ID from search results")


@tool(args_schema=HotelIdArgs)
def amadeus_get_hotel_details(hotel_id: str) -> str:
    """Get detailed information about a specific hotel."""
    return _json(hotels.get_hotel_details(_get_client(), hotel_id))


class SearchHotelByNameArgs(BaseModel):
    keyword: str = Field(description="Hotel name or partial name")
    max_results: int = Field(default=20, description="Maximum results")


@tool(args_schema=SearchHotelByNameArgs)
def amadeus_search_hotel_by_name(keyword: str, max_results: int = 20) -> str:
    """Search for hotels by name (autocomplete)."""
    return _json(hotels.search_hotel_by_name(_get_client(), keyword, max_results))


class HotelRatingsArgs(BaseModel):
    hotel_ids: str = Field(description="Comma-separated Amadeus hotel IDs")


@tool(args_schema=HotelRatingsArgs)
def amadeus_get_hotel_ratings(hotel_ids: str) -> str:
    """Get sentiment analysis ratings for hotels based on traveler reviews."""
    return _json(hotels.get_hotel_ratings(_get_client(), hotel_ids))


class BookHotelArgs(BaseModel):
    offer_id: str = Field(description="Hotel offer ID from search results")
    guests: str = Field(description="JSON array of guest details")
    payment: str = Field(description="JSON payment details")


@tool(args_schema=BookHotelArgs)
def amadeus_book_hotel(offer_id: str, guests: str, payment: str) -> str:
    """Book a hotel room."""
    return _json(hotels.book_hotel(
        _get_client(), offer_id, json.loads(guests), json.loads(payment),
    ))


# ── Airport/City tools ───────────────────────────────────────────────


class KeywordArgs(BaseModel):
    keyword: str = Field(description="City name or airport code to search")


@tool(args_schema=KeywordArgs)
def amadeus_search_airports(keyword: str) -> str:
    """Search for airports by city name or airport code."""
    return _json(airports.search_airports(_get_client(), keyword))


@tool(args_schema=KeywordArgs)
def amadeus_search_cities(keyword: str) -> str:
    """Search for cities by name."""
    return _json(airports.search_cities(_get_client(), keyword))


class AirportCodeArgs(BaseModel):
    airport_code: str = Field(description="Airport IATA code")


@tool(args_schema=AirportCodeArgs)
def amadeus_get_airport_routes(airport_code: str) -> str:
    """Get direct flight routes from an airport."""
    return _json(airports.get_airport_routes(_get_client(), airport_code))


class NearestAirportsArgs(BaseModel):
    latitude: float = Field(description="Latitude")
    longitude: float = Field(description="Longitude")
    radius: int = Field(default=100, description="Search radius in km (max 500)")
    max_results: int = Field(default=10, description="Maximum airports to return")


@tool(args_schema=NearestAirportsArgs)
def amadeus_get_nearest_airports(
    latitude: float,
    longitude: float,
    radius: int = 100,
    max_results: int = 10,
) -> str:
    """Find nearest airports to a geographical location."""
    return _json(airports.get_nearest_airports(
        _get_client(), latitude, longitude, radius, max_results,
    ))


class AirlineDestinationsArgs(BaseModel):
    airline_code: str = Field(description="IATA airline code (e.g., 'AA')")
    max_results: int = Field(default=50, description="Maximum destinations")


@tool(args_schema=AirlineDestinationsArgs)
def amadeus_get_airline_destinations(airline_code: str, max_results: int = 50) -> str:
    """Get all destinations served by a specific airline."""
    return _json(airports.get_airline_destinations(_get_client(), airline_code, max_results))


class AirportOnTimeArgs(BaseModel):
    airport_code: str = Field(description="IATA airport code")
    date: str = Field(description="Date to check (YYYY-MM-DD)")


@tool(args_schema=AirportOnTimeArgs)
def amadeus_get_airport_on_time_performance(airport_code: str, date: str) -> str:
    """Predict on-time performance for flights from an airport on a specific date."""
    return _json(airports.get_airport_on_time_performance(_get_client(), airport_code, date))


# ── Activity tools ───────────────────────────────────────────────────


class SearchActivitiesArgs(BaseModel):
    latitude: float = Field(description="Latitude")
    longitude: float = Field(description="Longitude")
    radius: int = Field(default=5, description="Search radius in km")


@tool(args_schema=SearchActivitiesArgs)
def amadeus_search_activities(latitude: float, longitude: float, radius: int = 5) -> str:
    """Search for tours and activities near a location."""
    return _json(activities.search_activities(_get_client(), latitude, longitude, radius))


class ActivityIdArgs(BaseModel):
    activity_id: str = Field(description="Activity ID from search results")


@tool(args_schema=ActivityIdArgs)
def amadeus_get_activity_details(activity_id: str) -> str:
    """Get detailed information about a specific activity."""
    return _json(activities.get_activity_details(_get_client(), activity_id))


# ── Transfer tools ───────────────────────────────────────────────────


class SearchTransfersArgs(BaseModel):
    start_latitude: float = Field(description="Pickup latitude")
    start_longitude: float = Field(description="Pickup longitude")
    end_latitude: float = Field(description="Dropoff latitude")
    end_longitude: float = Field(description="Dropoff longitude")
    transfer_date: str = Field(description="Date (YYYY-MM-DD)")
    transfer_time: str = Field(description="Time (HH:MM)")
    passengers: int = Field(default=1, description="Number of passengers")


@tool(args_schema=SearchTransfersArgs)
def amadeus_search_transfers(
    start_latitude: float,
    start_longitude: float,
    end_latitude: float,
    end_longitude: float,
    transfer_date: str,
    transfer_time: str,
    passengers: int = 1,
) -> str:
    """Search for ground transfer options between two locations."""
    return _json(transfers.search_transfers(
        _get_client(), start_latitude, start_longitude,
        end_latitude, end_longitude, transfer_date, transfer_time, passengers,
    ))


class BookTransferArgs(BaseModel):
    offer_id: str = Field(description="Transfer offer ID")
    passengers: str = Field(description="JSON array of passenger details")
    contact_email: str = Field(description="Contact email")
    contact_phone: str = Field(description="Contact phone with country code")


@tool(args_schema=BookTransferArgs)
def amadeus_book_transfer(
    offer_id: str,
    passengers: str,
    contact_email: str,
    contact_phone: str,
) -> str:
    """Book a ground transfer."""
    return _json(transfers.book_transfer(
        _get_client(), offer_id, json.loads(passengers), contact_email, contact_phone,
    ))


class TransferOrderIdArgs(BaseModel):
    order_id: str = Field(description="Transfer order ID")


@tool(args_schema=TransferOrderIdArgs)
def amadeus_get_transfer_order(order_id: str) -> str:
    """Get details of a transfer booking."""
    return _json(transfers.get_transfer_order(_get_client(), order_id))


@tool(args_schema=TransferOrderIdArgs)
def amadeus_cancel_transfer(order_id: str) -> str:
    """Cancel a transfer booking."""
    return _json(transfers.cancel_transfer(_get_client(), order_id))


# ── Analytics tools ──────────────────────────────────────────────────


class BusiestPeriodArgs(BaseModel):
    city_code: str = Field(description="IATA city code")
    year: str = Field(description="Year (YYYY)")
    direction: str = Field(default="ARRIVING", description="ARRIVING or DEPARTING")


@tool(args_schema=BusiestPeriodArgs)
def amadeus_get_busiest_travel_period(
    city_code: str, year: str, direction: str = "ARRIVING",
) -> str:
    """Get the busiest travel periods for a city."""
    return _json(analytics.get_busiest_travel_period(_get_client(), city_code, year, direction))


class TrafficArgs(BaseModel):
    origin_city: str = Field(description="IATA city code of origin")
    year: str = Field(description="Year (YYYY)")
    max_results: int = Field(default=20, description="Maximum destinations")


@tool(args_schema=TrafficArgs)
def amadeus_get_most_booked_destinations(
    origin_city: str, year: str, max_results: int = 20,
) -> str:
    """Get most booked flight destinations from a city."""
    return _json(analytics.get_most_booked_destinations(
        _get_client(), origin_city, year, max_results,
    ))


@tool(args_schema=TrafficArgs)
def amadeus_get_most_traveled_destinations(
    origin_city: str, year: str, max_results: int = 20,
) -> str:
    """Get most traveled flight destinations from a city (by passenger volume)."""
    return _json(analytics.get_most_traveled_destinations(
        _get_client(), origin_city, year, max_results,
    ))


class AnalyzeFlightPriceArgs(BaseModel):
    origin: str = Field(description="Origin airport IATA code")
    destination: str = Field(description="Destination airport IATA code")
    departure_date: str = Field(description="Departure date (YYYY-MM-DD)")
    return_date: Optional[str] = Field(default=None, description="Return date")


@tool(args_schema=AnalyzeFlightPriceArgs)
def amadeus_analyze_flight_price(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
) -> str:
    """Analyze if a flight price is good compared to historical data."""
    return _json(analytics.analyze_flight_price(
        _get_client(), origin, destination, departure_date, return_date,
    ))


class PredictDelayArgs(BaseModel):
    origin: str = Field(description="Origin airport IATA code")
    destination: str = Field(description="Destination airport IATA code")
    departure_date: str = Field(description="Departure date (YYYY-MM-DD)")
    departure_time: str = Field(description="Departure time (HH:MM:SS)")
    arrival_date: str = Field(description="Arrival date (YYYY-MM-DD)")
    arrival_time: str = Field(description="Arrival time (HH:MM:SS)")
    carrier_code: str = Field(description="IATA airline code")
    flight_number: str = Field(description="Flight number")
    aircraft_code: str = Field(description="ICAO aircraft code")
    duration: str = Field(description="Duration in ISO 8601 (e.g., 'PT3H30M')")


@tool(args_schema=PredictDelayArgs)
def amadeus_predict_flight_delay(
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
    """Predict the probability of flight delay."""
    return _json(analytics.predict_flight_delay(
        _get_client(), origin, destination, departure_date, departure_time,
        arrival_date, arrival_time, carrier_code, flight_number, aircraft_code, duration,
    ))


class PredictChoiceArgs(BaseModel):
    flight_offers: str = Field(description="JSON array of flight offers")


@tool(args_schema=PredictChoiceArgs)
def amadeus_predict_flight_choice(flight_offers: str) -> str:
    """Predict which flight offer travelers are most likely to choose."""
    return _json(analytics.predict_flight_choice(_get_client(), json.loads(flight_offers)))


class PredictTripPurposeArgs(BaseModel):
    origin: str = Field(description="Origin airport IATA code")
    destination: str = Field(description="Destination airport IATA code")
    departure_date: str = Field(description="Departure date (YYYY-MM-DD)")
    return_date: str = Field(description="Return date (YYYY-MM-DD)")
    search_date: Optional[str] = Field(default=None, description="Date of search (YYYY-MM-DD)")


@tool(args_schema=PredictTripPurposeArgs)
def amadeus_predict_trip_purpose(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str,
    search_date: Optional[str] = None,
) -> str:
    """Predict if a trip is for business or leisure."""
    return _json(analytics.predict_trip_purpose(
        _get_client(), origin, destination, departure_date, return_date, search_date,
    ))


# ── Order tools ──────────────────────────────────────────────────────


class CreateFlightOrderArgs(BaseModel):
    flight_offer: str = Field(description="JSON flight offer (from get_flight_price)")
    travelers: str = Field(description="JSON array of traveler details")
    contact_email: str = Field(description="Contact email")
    contact_phone: str = Field(description="Contact phone with country code")


@tool(args_schema=CreateFlightOrderArgs)
def amadeus_create_flight_order(
    flight_offer: str,
    travelers: str,
    contact_email: str,
    contact_phone: str,
) -> str:
    """Create a flight booking order."""
    return _json(orders.create_flight_order(
        _get_client(), json.loads(flight_offer), json.loads(travelers),
        contact_email, contact_phone,
    ))


class FlightOrderIdArgs(BaseModel):
    order_id: str = Field(description="Flight order ID")


@tool(args_schema=FlightOrderIdArgs)
def amadeus_get_flight_order(order_id: str) -> str:
    """Retrieve details of an existing flight order."""
    return _json(orders.get_flight_order(_get_client(), order_id))


@tool(args_schema=FlightOrderIdArgs)
def amadeus_cancel_flight_order(order_id: str) -> str:
    """Cancel an existing flight order."""
    return _json(orders.cancel_flight_order(_get_client(), order_id))


# ── Misc tools ───────────────────────────────────────────────────────


class TravelRecsArgs(BaseModel):
    city_code: str = Field(description="City IATA code")
    category: str = Field(default="SIGHTS", description="SIGHTS, NIGHTLIFE, RESTAURANT, SHOPPING")


@tool(args_schema=TravelRecsArgs)
def amadeus_get_travel_recommendations(city_code: str, category: str = "SIGHTS") -> str:
    """Get travel recommendations for a city."""
    return _json(misc.get_travel_recommendations(_get_client(), city_code, category))


class RecommendedDestsArgs(BaseModel):
    origin_cities: str = Field(description="Comma-separated IATA city codes")
    traveler_interest: str = Field(default="ADVENTURE", description="Interest category")


@tool(args_schema=RecommendedDestsArgs)
def amadeus_get_recommended_destinations(
    origin_cities: str, traveler_interest: str = "ADVENTURE",
) -> str:
    """Get destination recommendations based on traveler interests."""
    return _json(misc.get_recommended_destinations(
        _get_client(), origin_cities, traveler_interest,
    ))


class ParseTripDocArgs(BaseModel):
    document_content: str = Field(description="Base64-encoded document content")
    document_type: str = Field(default="HTML", description="HTML, EML, or PDF")


@tool(args_schema=ParseTripDocArgs)
def amadeus_parse_trip_document(document_content: str, document_type: str = "HTML") -> str:
    """Parse a booking confirmation to extract structured trip data."""
    return _json(misc.parse_trip_document(_get_client(), document_content, document_type))


class DocumentIdArgs(BaseModel):
    document_id: str = Field(description="Document ID from parse_trip_document")


@tool(args_schema=DocumentIdArgs)
def amadeus_get_parsed_trip(document_id: str) -> str:
    """Get the parsed trip data from a previously submitted document."""
    return _json(misc.get_parsed_trip(_get_client(), document_id))


# ── Exported list ────────────────────────────────────────────────────

TOOLS: list[BaseTool] = [
    # Flights (7)
    amadeus_search_flights,
    amadeus_get_flight_price,
    amadeus_search_flight_inspiration,
    amadeus_search_flight_availability,
    amadeus_get_branded_fares,
    amadeus_get_seatmap,
    amadeus_get_flight_status,
    # Hotels (5)
    amadeus_search_hotels,
    amadeus_get_hotel_details,
    amadeus_search_hotel_by_name,
    amadeus_get_hotel_ratings,
    amadeus_book_hotel,
    # Airports (6)
    amadeus_search_airports,
    amadeus_search_cities,
    amadeus_get_airport_routes,
    amadeus_get_nearest_airports,
    amadeus_get_airline_destinations,
    amadeus_get_airport_on_time_performance,
    # Activities (2)
    amadeus_search_activities,
    amadeus_get_activity_details,
    # Transfers (4)
    amadeus_search_transfers,
    amadeus_book_transfer,
    amadeus_get_transfer_order,
    amadeus_cancel_transfer,
    # Analytics (7)
    amadeus_get_busiest_travel_period,
    amadeus_get_most_booked_destinations,
    amadeus_get_most_traveled_destinations,
    amadeus_analyze_flight_price,
    amadeus_predict_flight_delay,
    amadeus_predict_flight_choice,
    amadeus_predict_trip_purpose,
    # Orders (3)
    amadeus_create_flight_order,
    amadeus_get_flight_order,
    amadeus_cancel_flight_order,
    # Misc (4)
    amadeus_get_travel_recommendations,
    amadeus_get_recommended_destinations,
    amadeus_parse_trip_document,
    amadeus_get_parsed_trip,
]
