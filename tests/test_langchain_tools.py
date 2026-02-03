"""Tests for Amadeus LangChain tool interfaces."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from mcp_amadeus.langchain_tools import (
    TOOLS,
    amadeus_search_flights,
    amadeus_get_flight_price,
    amadeus_search_hotels,
    amadeus_search_airports,
    amadeus_search_activities,
    amadeus_search_transfers,
    amadeus_get_busiest_travel_period,
    amadeus_create_flight_order,
    amadeus_get_travel_recommendations,
    amadeus_predict_trip_purpose,
    amadeus_cancel_flight_order,
    amadeus_get_parsed_trip,
)


class TestToolList:
    def test_tools_list_has_38_tools(self):
        assert len(TOOLS) == 38

    def test_all_tools_have_names(self):
        for tool in TOOLS:
            assert tool.name is not None
            assert tool.name.startswith("amadeus_")

    def test_all_tools_have_descriptions(self):
        for tool in TOOLS:
            assert tool.description is not None
            assert len(tool.description) > 0

    def test_tool_names_are_unique(self):
        names = [t.name for t in TOOLS]
        assert len(names) == len(set(names))


class TestToolInvocation:
    """Test that tools delegate to ops layer correctly by mocking ops modules."""

    @patch("mcp_amadeus.langchain_tools.flights")
    @patch("mcp_amadeus.langchain_tools._get_client")
    def test_search_flights(self, mock_get_client, mock_flights):
        mock_flights.search_flights.return_value = [
            {"id": "1", "price": {"total": "350.00"}}
        ]

        result = amadeus_search_flights.invoke({
            "origin": "JFK",
            "destination": "LAX",
            "departure_date": "2025-06-01",
        })

        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert parsed[0]["id"] == "1"

    @patch("mcp_amadeus.langchain_tools.flights")
    @patch("mcp_amadeus.langchain_tools._get_client")
    def test_get_flight_price(self, mock_get_client, mock_flights):
        mock_flights.get_flight_price.return_value = {"total_price": "350.00"}

        result = amadeus_get_flight_price.invoke({
            "flight_offer": '{"id": "1"}',
        })

        parsed = json.loads(result)
        assert parsed["total_price"] == "350.00"
        # Verify JSON was parsed before passing to ops
        call_args = mock_flights.get_flight_price.call_args
        assert call_args[0][1] == {"id": "1"}

    @patch("mcp_amadeus.langchain_tools.hotels")
    @patch("mcp_amadeus.langchain_tools._get_client")
    def test_search_hotels(self, mock_get_client, mock_hotels):
        mock_hotels.search_hotels.return_value = [
            {"hotel_id": "H1", "name": "Test Hotel"}
        ]

        result = amadeus_search_hotels.invoke({
            "city_code": "NYC",
            "check_in": "2025-06-01",
            "check_out": "2025-06-05",
        })

        parsed = json.loads(result)
        assert parsed[0]["hotel_id"] == "H1"

    @patch("mcp_amadeus.langchain_tools.airports")
    @patch("mcp_amadeus.langchain_tools._get_client")
    def test_search_airports(self, mock_get_client, mock_airports):
        mock_airports.search_airports.return_value = [
            {"iata_code": "JFK", "name": "JFK Airport"}
        ]

        result = amadeus_search_airports.invoke({"keyword": "New York"})

        parsed = json.loads(result)
        assert parsed[0]["iata_code"] == "JFK"

    @patch("mcp_amadeus.langchain_tools.activities")
    @patch("mcp_amadeus.langchain_tools._get_client")
    def test_search_activities(self, mock_get_client, mock_activities):
        mock_activities.search_activities.return_value = [
            {"id": "A1", "name": "City Tour"}
        ]

        result = amadeus_search_activities.invoke({
            "latitude": 48.8,
            "longitude": 2.3,
        })

        parsed = json.loads(result)
        assert parsed[0]["name"] == "City Tour"

    @patch("mcp_amadeus.langchain_tools.transfers")
    @patch("mcp_amadeus.langchain_tools._get_client")
    def test_search_transfers(self, mock_get_client, mock_transfers):
        mock_transfers.search_transfers.return_value = [
            {"offer_id": "T1", "transfer_type": "PRIVATE"}
        ]

        result = amadeus_search_transfers.invoke({
            "start_latitude": 48.8,
            "start_longitude": 2.3,
            "end_latitude": 48.9,
            "end_longitude": 2.4,
            "transfer_date": "2025-06-01",
            "transfer_time": "14:00",
        })

        parsed = json.loads(result)
        assert parsed[0]["offer_id"] == "T1"

    @patch("mcp_amadeus.langchain_tools.analytics")
    @patch("mcp_amadeus.langchain_tools._get_client")
    def test_get_busiest_travel_period(self, mock_get_client, mock_analytics):
        mock_analytics.get_busiest_travel_period.return_value = {
            "city": "NYC",
            "year": "2025",
            "periods": [{"period": "2025-07"}],
        }

        result = amadeus_get_busiest_travel_period.invoke({
            "city_code": "NYC",
            "year": "2025",
        })

        parsed = json.loads(result)
        assert parsed["city"] == "NYC"

    @patch("mcp_amadeus.langchain_tools.orders")
    @patch("mcp_amadeus.langchain_tools._get_client")
    def test_create_flight_order(self, mock_get_client, mock_orders):
        mock_orders.create_flight_order.return_value = {
            "order_id": "FO1",
            "booking_reference": "ABC123",
        }

        result = amadeus_create_flight_order.invoke({
            "flight_offer": '{"id": "1"}',
            "travelers": '[{"id": "1"}]',
            "contact_email": "test@test.com",
            "contact_phone": "+1234567890",
        })

        parsed = json.loads(result)
        assert parsed["order_id"] == "FO1"

    @patch("mcp_amadeus.langchain_tools.orders")
    @patch("mcp_amadeus.langchain_tools._get_client")
    def test_cancel_flight_order(self, mock_get_client, mock_orders):
        mock_orders.cancel_flight_order.return_value = {
            "message": "Order FO1 cancelled successfully"
        }

        result = amadeus_cancel_flight_order.invoke({"order_id": "FO1"})

        parsed = json.loads(result)
        assert "cancelled" in parsed["message"]

    @patch("mcp_amadeus.langchain_tools.misc")
    @patch("mcp_amadeus.langchain_tools._get_client")
    def test_get_travel_recommendations(self, mock_get_client, mock_misc):
        mock_misc.get_travel_recommendations.return_value = [
            {"name": "Eiffel Tower", "category": "SIGHTS"}
        ]

        result = amadeus_get_travel_recommendations.invoke({
            "city_code": "PAR",
        })

        parsed = json.loads(result)
        assert parsed[0]["name"] == "Eiffel Tower"

    @patch("mcp_amadeus.langchain_tools.analytics")
    @patch("mcp_amadeus.langchain_tools._get_client")
    def test_predict_trip_purpose(self, mock_get_client, mock_analytics):
        mock_analytics.predict_trip_purpose.return_value = {
            "predicted_purpose": "LEISURE",
            "leisure_probability": 0.7,
        }

        result = amadeus_predict_trip_purpose.invoke({
            "origin": "JFK",
            "destination": "CUN",
            "departure_date": "2025-06-01",
            "return_date": "2025-06-08",
        })

        parsed = json.loads(result)
        assert parsed["predicted_purpose"] == "LEISURE"

    @patch("mcp_amadeus.langchain_tools.misc")
    @patch("mcp_amadeus.langchain_tools._get_client")
    def test_get_parsed_trip(self, mock_get_client, mock_misc):
        mock_misc.get_parsed_trip.return_value = {
            "document_id": "D1",
            "status": "COMPLETED",
            "trips": [{"type": "FLIGHT"}],
        }

        result = amadeus_get_parsed_trip.invoke({"document_id": "D1"})

        parsed = json.loads(result)
        assert parsed["status"] == "COMPLETED"
