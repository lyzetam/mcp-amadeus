"""Ground transfer operations."""

from __future__ import annotations

import json

from ..client import AmadeusClient


def search_transfers(
    client: AmadeusClient,
    start_latitude: float,
    start_longitude: float,
    end_latitude: float,
    end_longitude: float,
    transfer_date: str,
    transfer_time: str,
    passengers: int = 1,
) -> list[dict]:
    """Search for ground transfer options between two locations."""
    request_body = {
        "startLocationCode": f"{start_latitude},{start_longitude}",
        "endGeoCode": f"{end_latitude},{end_longitude}",
        "transferType": "PRIVATE",
        "startDateTime": f"{transfer_date}T{transfer_time}:00",
        "passengers": passengers,
    }
    data = client.request("POST", "/v1/shopping/transfer-offers", json_data=request_body)

    result = []
    for offer in data.get("data", [])[:10]:
        result.append({
            "offer_id": offer.get("id"),
            "transfer_type": offer.get("transferType"),
            "vehicle": offer.get("vehicle"),
            "price": offer.get("quotation"),
            "duration": offer.get("duration"),
            "cancellation_policy": offer.get("cancellationRules"),
        })
    return result


def book_transfer(
    client: AmadeusClient,
    offer_id: str,
    passengers: list[dict],
    contact_email: str,
    contact_phone: str,
) -> dict:
    """Book a ground transfer."""
    request_body = {
        "data": {
            "type": "transfer-order",
            "offerId": offer_id,
            "passengers": passengers,
            "contacts": [{"emailAddress": contact_email, "phoneNumber": contact_phone}],
        }
    }
    data = client.request("POST", "/v1/booking/transfer-orders", json_data=request_body)
    result = data.get("data", {})
    return {
        "order_id": result.get("id"),
        "confirmation_number": result.get("confirmationNumber"),
        "status": result.get("status"),
    }


def get_transfer_order(client: AmadeusClient, order_id: str) -> dict:
    """Get details of a transfer booking."""
    data = client.request("GET", f"/v1/booking/transfer-orders/{order_id}")
    result = data.get("data", {})
    return {
        "order_id": result.get("id"),
        "confirmation_number": result.get("confirmationNumber"),
        "status": result.get("status"),
        "transfer_details": result.get("transferDetails"),
        "passengers": result.get("passengers"),
    }


def cancel_transfer(client: AmadeusClient, order_id: str) -> dict:
    """Cancel a transfer booking."""
    result = client.delete_request(f"/v1/booking/transfer-orders/{order_id}")
    if result.get("status") == "success":
        return {"message": f"Transfer {order_id} cancelled successfully"}
    return {"message": "Cancellation processed", "response": result}
