"""Tests for Amadeus operations layer using mocked AmadeusClient."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from mcp_amadeus.client import AmadeusClient
from mcp_amadeus.operations import (
    flights, hotels, airports, activities, transfers, analytics, orders, misc,
)


# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def mock_client():
    """Create an AmadeusClient with mocked request methods."""
    client = AmadeusClient.__new__(AmadeusClient)
    client.client_id = "test_id"
    client.client_secret = "test_secret"
    client.base_url = "https://test.api.amadeus.com"
    client._access_token = "mock_token"
    client._token_expiry = None
    client.request = MagicMock()
    client.delete_request = MagicMock()
    return client


# ── Flight tests ─────────────────────────────────────────────────────


class TestSearchFlights:
    def test_returns_formatted_offers(self, mock_client):
        mock_client.request.return_value = {
            "data": [
                {
                    "id": "1",
                    "price": {"total": "350.00", "currency": "USD"},
                    "itineraries": [
                        {
                            "duration": "PT5H30M",
                            "segments": [
                                {
                                    "departure": {"iataCode": "JFK", "at": "2025-06-01T08:00"},
                                    "arrival": {"iataCode": "LAX", "at": "2025-06-01T11:30"},
                                    "carrierCode": "AA",
                                    "number": "123",
                                    "duration": "PT5H30M",
                                }
                            ],
                        }
                    ],
                    "numberOfBookableSeats": 9,
                }
            ]
        }

        result = flights.search_flights(mock_client, "JFK", "LAX", "2025-06-01")

        assert len(result) == 1
        assert result[0]["id"] == "1"
        assert result[0]["price"]["total"] == "350.00"
        assert result[0]["itineraries"][0]["segments"][0]["carrier"] == "AA"

    def test_empty_results(self, mock_client):
        mock_client.request.return_value = {"data": []}
        result = flights.search_flights(mock_client, "JFK", "LAX", "2025-06-01")
        assert result == []


class TestGetFlightPrice:
    def test_returns_price(self, mock_client):
        mock_client.request.return_value = {
            "data": {
                "flightOffers": [
                    {
                        "price": {"total": "350.00"},
                        "travelerPricings": [{"travelerId": "1", "price": {"total": "350.00"}}],
                    }
                ]
            }
        }

        result = flights.get_flight_price(mock_client, {"id": "1"})

        assert result["total_price"] == "350.00"


class TestSearchFlightInspiration:
    def test_returns_destinations(self, mock_client):
        mock_client.request.return_value = {
            "data": [
                {
                    "destination": "LAX",
                    "departureDate": "2025-06-15",
                    "returnDate": "2025-06-22",
                    "price": {"total": "200.00"},
                }
            ]
        }

        result = flights.search_flight_inspiration(mock_client, "JFK")

        assert len(result) == 1
        assert result[0]["destination"] == "LAX"


class TestFlightStatus:
    def test_returns_status(self, mock_client):
        mock_client.request.return_value = {
            "data": [
                {
                    "flightPoints": [
                        {
                            "iataCode": "JFK",
                            "departure": {"terminal": "8", "at": "2025-06-01T08:00"},
                        },
                        {
                            "iataCode": "LAX",
                            "arrival": {"terminal": "4", "at": "2025-06-01T11:30"},
                        },
                    ],
                    "flightDesignator": {"aircraftType": "738"},
                    "duration": "PT5H30M",
                }
            ]
        }

        result = flights.get_flight_status(mock_client, "AA", "123", "2025-06-01")

        assert len(result) == 1
        assert result[0]["flight"] == "AA123"
        assert result[0]["departure"]["airport"] == "JFK"


# ── Hotel tests ──────────────────────────────────────────────────────


class TestSearchHotels:
    def test_returns_sorted_hotels(self, mock_client):
        # First call: hotel list
        mock_client.request.side_effect = [
            {"data": [{"hotelId": "H1"}, {"hotelId": "H2"}]},
            {
                "data": [
                    {
                        "hotel": {"hotelId": "H1", "name": "Hotel A", "rating": "4"},
                        "offers": [{"id": "O1", "price": {"total": "200", "currency": "USD"}, "room": {"typeEstimated": {"category": "STANDARD"}}}],
                    },
                    {
                        "hotel": {"hotelId": "H2", "name": "Hotel B", "rating": "5"},
                        "offers": [{"id": "O2", "price": {"total": "150", "currency": "USD"}, "room": {"typeEstimated": {"category": "DELUXE"}}}],
                    },
                ]
            },
        ]

        result = hotels.search_hotels(mock_client, "NYC", "2025-06-01", "2025-06-05")

        assert len(result) == 2
        # Sorted by price - cheapest first
        assert result[0]["name"] == "Hotel B"

    def test_no_hotels_found(self, mock_client):
        mock_client.request.return_value = {"data": []}
        result = hotels.search_hotels(mock_client, "XXX", "2025-06-01", "2025-06-05")
        assert result == []


class TestGetHotelDetails:
    def test_returns_details(self, mock_client):
        mock_client.request.return_value = {
            "data": [
                {
                    "hotel": {
                        "hotelId": "H1",
                        "name": "Test Hotel",
                        "rating": "4",
                        "description": {"text": "A nice hotel"},
                        "amenities": ["WIFI", "POOL"],
                    },
                    "offers": [{"id": "O1", "checkInDate": "2025-06-01"}],
                }
            ]
        }

        result = hotels.get_hotel_details(mock_client, "H1")

        assert result["name"] == "Test Hotel"
        assert "WIFI" in result["amenities"]


class TestSearchHotelByName:
    def test_returns_matches(self, mock_client):
        mock_client.request.return_value = {
            "data": [{"hotelId": "H1", "name": "Hilton NYC", "address": {"cityName": "New York"}}]
        }

        result = hotels.search_hotel_by_name(mock_client, "Hilton")

        assert len(result) == 1
        assert result[0]["name"] == "Hilton NYC"


class TestGetHotelRatings:
    def test_returns_ratings(self, mock_client):
        mock_client.request.return_value = {
            "data": [
                {
                    "hotelId": "H1",
                    "overallRating": 85,
                    "numberOfReviews": 500,
                    "sentimentScores": {"location": 90, "comfort": 80, "service": 85},
                }
            ]
        }

        result = hotels.get_hotel_ratings(mock_client, "H1")

        assert result[0]["overall_rating"] == 85


class TestBookHotel:
    def test_returns_booking(self, mock_client):
        mock_client.request.return_value = {
            "data": [{"id": "B1", "providerConfirmationId": "CF123", "bookingStatus": "CONFIRMED"}]
        }

        result = hotels.book_hotel(mock_client, "O1", [{"name": {"firstName": "John"}}], {"method": "CARD"})

        assert result["booking_id"] == "B1"
        assert result["status"] == "CONFIRMED"


# ── Airport tests ────────────────────────────────────────────────────


class TestSearchAirports:
    def test_returns_airports(self, mock_client):
        mock_client.request.return_value = {
            "data": [
                {
                    "iataCode": "JFK",
                    "name": "John F Kennedy International",
                    "address": {"cityName": "New York", "countryName": "United States"},
                }
            ]
        }

        result = airports.search_airports(mock_client, "New York")

        assert result[0]["iata_code"] == "JFK"


class TestSearchCities:
    def test_returns_cities(self, mock_client):
        mock_client.request.return_value = {
            "data": [{"iataCode": "NYC", "name": "New York", "address": {"countryName": "United States"}}]
        }

        result = airports.search_cities(mock_client, "New York")

        assert result[0]["iata_code"] == "NYC"


class TestGetAirportRoutes:
    def test_returns_routes(self, mock_client):
        mock_client.request.return_value = {
            "data": [{"destination": "LAX", "name": "Los Angeles"}]
        }

        result = airports.get_airport_routes(mock_client, "JFK")

        assert result[0]["destination"] == "LAX"


class TestGetNearestAirports:
    def test_returns_nearby(self, mock_client):
        mock_client.request.return_value = {
            "data": [
                {
                    "iataCode": "JFK",
                    "name": "JFK Airport",
                    "address": {"cityName": "New York", "countryName": "US"},
                    "distance": {"value": 15.2},
                    "geoCode": {"latitude": 40.6, "longitude": -73.7},
                }
            ]
        }

        result = airports.get_nearest_airports(mock_client, 40.7, -73.9)

        assert result[0]["distance_km"] == 15.2


class TestGetAirlineDestinations:
    def test_returns_destinations(self, mock_client):
        mock_client.request.return_value = {
            "data": [{"name": "Paris", "iataCode": "CDG", "subtype": "city"}]
        }

        result = airports.get_airline_destinations(mock_client, "AF")

        assert result[0]["city"] == "Paris"


class TestGetAirportOnTime:
    def test_returns_prediction(self, mock_client):
        mock_client.request.return_value = {
            "data": {"probability": 0.85, "result": "HIGH"}
        }

        result = airports.get_airport_on_time_performance(mock_client, "JFK", "2025-06-01")

        assert result["on_time_probability"] == 0.85


# ── Activity tests ───────────────────────────────────────────────────


class TestSearchActivities:
    def test_returns_activities(self, mock_client):
        mock_client.request.return_value = {
            "data": [
                {
                    "id": "A1",
                    "name": "City Tour",
                    "shortDescription": "Amazing tour",
                    "rating": "4.5",
                    "price": {"amount": "50.00"},
                }
            ]
        }

        result = activities.search_activities(mock_client, 48.8, 2.3)

        assert result[0]["name"] == "City Tour"


class TestGetActivityDetails:
    def test_returns_details(self, mock_client):
        mock_client.request.return_value = {
            "data": {"id": "A1", "name": "City Tour", "description": "Full day tour"}
        }

        result = activities.get_activity_details(mock_client, "A1")

        assert result["name"] == "City Tour"


# ── Transfer tests ───────────────────────────────────────────────────


class TestSearchTransfers:
    def test_returns_offers(self, mock_client):
        mock_client.request.return_value = {
            "data": [
                {
                    "id": "T1",
                    "transferType": "PRIVATE",
                    "vehicle": {"category": "SEDAN"},
                    "quotation": {"amount": "75.00"},
                }
            ]
        }

        result = transfers.search_transfers(
            mock_client, 48.8, 2.3, 48.9, 2.4, "2025-06-01", "14:00"
        )

        assert result[0]["offer_id"] == "T1"


class TestBookTransfer:
    def test_returns_booking(self, mock_client):
        mock_client.request.return_value = {
            "data": {"id": "TO1", "confirmationNumber": "TC123", "status": "CONFIRMED"}
        }

        result = transfers.book_transfer(
            mock_client, "T1", [{"firstName": "John"}], "john@test.com", "+1234567890"
        )

        assert result["order_id"] == "TO1"


class TestGetTransferOrder:
    def test_returns_order(self, mock_client):
        mock_client.request.return_value = {
            "data": {"id": "TO1", "confirmationNumber": "TC123", "status": "CONFIRMED"}
        }

        result = transfers.get_transfer_order(mock_client, "TO1")

        assert result["status"] == "CONFIRMED"


class TestCancelTransfer:
    def test_successful_cancel(self, mock_client):
        mock_client.delete_request.return_value = {"status": "success"}

        result = transfers.cancel_transfer(mock_client, "TO1")

        assert "cancelled successfully" in result["message"]


# ── Analytics tests ──────────────────────────────────────────────────


class TestGetBusiestTravelPeriod:
    def test_returns_periods(self, mock_client):
        mock_client.request.return_value = {
            "data": [{"period": "2025-07", "analytics": {"travelers": "25.3"}}]
        }

        result = analytics.get_busiest_travel_period(mock_client, "NYC", "2025")

        assert result["city"] == "NYC"
        assert len(result["periods"]) == 1


class TestGetMostBookedDestinations:
    def test_returns_destinations(self, mock_client):
        mock_client.request.return_value = {
            "data": [{"destination": "LON", "analytics": {"flights": "12.5", "travelers": "15.2"}}]
        }

        result = analytics.get_most_booked_destinations(mock_client, "NYC", "2025")

        assert result["destinations"][0]["destination"] == "LON"


class TestGetMostTraveledDestinations:
    def test_returns_destinations(self, mock_client):
        mock_client.request.return_value = {
            "data": [{"destination": "PAR", "analytics": {"flights": "10.0", "travelers": "20.0"}}]
        }

        result = analytics.get_most_traveled_destinations(mock_client, "NYC", "2025")

        assert result["destinations"][0]["destination"] == "PAR"


class TestAnalyzeFlightPrice:
    def test_returns_analysis(self, mock_client):
        mock_client.request.return_value = {
            "data": {"analytics": {"averagePrice": "350.00"}}
        }

        result = analytics.analyze_flight_price(mock_client, "JFK", "LAX", "2025-06-01")

        assert result["average_price"] == "350.00"


class TestPredictFlightDelay:
    def test_returns_prediction(self, mock_client):
        mock_client.request.return_value = {
            "data": {"result": "LOW", "probability": {"LOW": 0.85, "HIGH": 0.15}}
        }

        result = analytics.predict_flight_delay(
            mock_client, "JFK", "LAX", "2025-06-01", "08:00:00",
            "2025-06-01", "11:30:00", "AA", "123", "738", "PT5H30M",
        )

        assert result["prediction_result"] == "LOW"


class TestPredictFlightChoice:
    def test_returns_predictions(self, mock_client):
        mock_client.request.return_value = {
            "data": [{"id": "1", "choicePrediction": {"score": 0.8}}]
        }

        result = analytics.predict_flight_choice(mock_client, [{"id": "1"}])

        assert result[0]["choice_probability"] == 0.8


class TestPredictTripPurpose:
    def test_returns_purpose(self, mock_client):
        mock_client.request.return_value = {
            "data": {
                "result": "LEISURE",
                "probabilities": {"BUSINESS": 0.3, "LEISURE": 0.7},
            }
        }

        result = analytics.predict_trip_purpose(
            mock_client, "JFK", "CUN", "2025-06-01", "2025-06-08"
        )

        assert result["predicted_purpose"] == "LEISURE"
        assert result["leisure_probability"] == 0.7


# ── Order tests ──────────────────────────────────────────────────────


class TestCreateFlightOrder:
    def test_returns_order(self, mock_client):
        mock_client.request.return_value = {
            "data": {
                "id": "FO1",
                "associatedRecords": [{"reference": "ABC123"}],
                "creationDate": "2025-06-01",
            }
        }

        result = orders.create_flight_order(
            mock_client, {"id": "1"}, [{"id": "1"}], "test@test.com", "+1234567890"
        )

        assert result["order_id"] == "FO1"
        assert result["booking_reference"] == "ABC123"


class TestGetFlightOrder:
    def test_returns_order(self, mock_client):
        mock_client.request.return_value = {
            "data": {
                "id": "FO1",
                "status": "CONFIRMED",
                "associatedRecords": [{"reference": "ABC123"}],
            }
        }

        result = orders.get_flight_order(mock_client, "FO1")

        assert result["status"] == "CONFIRMED"


class TestCancelFlightOrder:
    def test_successful_cancel(self, mock_client):
        mock_client.delete_request.return_value = {"status": "success"}

        result = orders.cancel_flight_order(mock_client, "FO1")

        assert "cancelled successfully" in result["message"]


# ── Misc tests ───────────────────────────────────────────────────────


class TestGetTravelRecommendations:
    def test_returns_pois(self, mock_client):
        mock_client.request.return_value = {
            "data": [{"name": "Eiffel Tower", "category": "SIGHTS", "rank": 1}]
        }

        result = misc.get_travel_recommendations(mock_client, "PAR")

        assert result[0]["name"] == "Eiffel Tower"

    def test_handles_error(self, mock_client):
        mock_client.request.side_effect = Exception("API error")

        result = misc.get_travel_recommendations(mock_client, "PAR")

        assert "not available" in result[0]["message"]


class TestGetRecommendedDestinations:
    def test_returns_recommendations(self, mock_client):
        mock_client.request.return_value = {
            "data": [
                {
                    "name": "Barcelona",
                    "iataCode": "BCN",
                    "address": {"countryName": "Spain"},
                    "score": 85,
                }
            ]
        }

        result = misc.get_recommended_destinations(mock_client, "PAR")

        assert result["recommendations"][0]["destination"] == "Barcelona"


class TestParseTripDocument:
    def test_returns_job(self, mock_client):
        mock_client.request.return_value = {
            "data": {"id": "D1", "status": "PROCESSING", "trips": []}
        }

        result = misc.parse_trip_document(mock_client, "base64content")

        assert result["job_id"] == "D1"
        assert result["status"] == "PROCESSING"


class TestGetParsedTrip:
    def test_returns_parsed(self, mock_client):
        mock_client.request.return_value = {
            "data": {"id": "D1", "status": "COMPLETED", "trips": [{"type": "FLIGHT"}]}
        }

        result = misc.get_parsed_trip(mock_client, "D1")

        assert result["status"] == "COMPLETED"
        assert len(result["trips"]) == 1
