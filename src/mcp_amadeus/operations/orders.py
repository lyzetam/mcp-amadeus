"""Flight booking order operations."""

from __future__ import annotations

import json

from ..client import AmadeusClient


def create_flight_order(
    client: AmadeusClient,
    flight_offer: dict,
    travelers: list[dict],
    contact_email: str,
    contact_phone: str,
) -> dict:
    """Create a flight booking order."""
    request_body = {
        "data": {
            "type": "flight-order",
            "flightOffers": [flight_offer],
            "travelers": travelers,
            "remarks": {
                "general": [{"subType": "GENERAL_MISCELLANEOUS", "text": "BOOKED VIA MCP"}]
            },
            "ticketingAgreement": {"option": "DELAY_TO_QUEUE"},
            "contacts": [
                {
                    "emailAddress": contact_email,
                    "phones": [{"deviceType": "MOBILE", "number": contact_phone}],
                    "purpose": "STANDARD",
                }
            ],
        }
    }
    data = client.request("POST", "/v1/booking/flight-orders", json_data=request_body)
    result = data.get("data", {})
    records = result.get("associatedRecords", [{}])
    return {
        "order_id": result.get("id"),
        "booking_reference": records[0].get("reference") if records else None,
        "creation_date": result.get("creationDate"),
        "travelers": result.get("travelers"),
        "flight_offers": result.get("flightOffers"),
    }


def get_flight_order(client: AmadeusClient, order_id: str) -> dict:
    """Retrieve details of an existing flight order."""
    data = client.request("GET", f"/v1/booking/flight-orders/{order_id}")
    result = data.get("data", {})
    records = result.get("associatedRecords", [{}])
    return {
        "order_id": result.get("id"),
        "booking_reference": records[0].get("reference") if records else None,
        "status": result.get("status"),
        "travelers": result.get("travelers"),
        "flight_offers": result.get("flightOffers"),
        "ticketing": result.get("ticketingAgreement"),
    }


def cancel_flight_order(client: AmadeusClient, order_id: str) -> dict:
    """Cancel an existing flight order."""
    result = client.delete_request(f"/v1/booking/flight-orders/{order_id}")
    if result.get("status") == "success":
        return {"message": f"Order {order_id} cancelled successfully"}
    return {"message": "Cancellation processed", "response": result}
