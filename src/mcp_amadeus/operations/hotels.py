"""Hotel search, details, ratings, and booking operations."""

from __future__ import annotations

import json
from typing import Optional

from ..client import AmadeusClient


def search_hotels(
    client: AmadeusClient,
    city_code: str,
    check_in: str,
    check_out: str,
    adults: int = 1,
    rooms: int = 1,
    radius: int = 5,
    max_results: int = 10,
) -> list[dict]:
    """Search for hotels in a city."""
    params = {
        "cityCode": city_code.upper(),
        "radius": radius,
        "radiusUnit": "KM",
    }
    hotels_data = client.request(
        "GET", "/v1/reference-data/locations/hotels/by-city", params=params
    )
    hotel_ids = [h.get("hotelId") for h in hotels_data.get("data", [])[:max_results]]

    if not hotel_ids:
        return []

    offers_params = {
        "hotelIds": ",".join(hotel_ids),
        "checkInDate": check_in,
        "checkOutDate": check_out,
        "adults": adults,
        "roomQuantity": rooms,
        "currency": "USD",
    }
    offers_data = client.request("GET", "/v3/shopping/hotel-offers", params=offers_params)

    result = []
    for hotel in offers_data.get("data", []):
        hotel_info = hotel.get("hotel", {})
        offers = hotel.get("offers", [])
        if offers:
            cheapest = min(
                offers, key=lambda x: float(x.get("price", {}).get("total", 999999))
            )
            result.append({
                "hotel_id": hotel_info.get("hotelId"),
                "name": hotel_info.get("name"),
                "rating": hotel_info.get("rating"),
                "latitude": hotel_info.get("latitude"),
                "longitude": hotel_info.get("longitude"),
                "price": {
                    "total": cheapest.get("price", {}).get("total"),
                    "currency": cheapest.get("price", {}).get("currency"),
                },
                "room_type": cheapest.get("room", {}).get("typeEstimated", {}).get("category"),
                "offer_id": cheapest.get("id"),
            })
    return sorted(result, key=lambda x: float(x.get("price", {}).get("total", 0)))


def get_hotel_details(client: AmadeusClient, hotel_id: str) -> dict:
    """Get detailed information about a specific hotel."""
    data = client.request("GET", "/v3/shopping/hotel-offers", params={"hotelIds": hotel_id})
    hotels = data.get("data", [])
    if not hotels:
        return {"message": "Hotel not found"}

    hotel = hotels[0]
    hotel_info = hotel.get("hotel", {})
    return {
        "hotel_id": hotel_info.get("hotelId"),
        "name": hotel_info.get("name"),
        "description": hotel_info.get("description", {}).get("text"),
        "rating": hotel_info.get("rating"),
        "address": hotel_info.get("address"),
        "contact": hotel_info.get("contact"),
        "amenities": hotel_info.get("amenities", []),
        "offers": [
            {
                "id": offer.get("id"),
                "check_in": offer.get("checkInDate"),
                "check_out": offer.get("checkOutDate"),
                "room": offer.get("room"),
                "price": offer.get("price"),
                "cancellation": offer.get("policies", {}).get("cancellation"),
            }
            for offer in hotel.get("offers", [])
        ],
    }


def search_hotel_by_name(
    client: AmadeusClient,
    keyword: str,
    max_results: int = 20,
) -> list[dict]:
    """Search for hotels by name (autocomplete)."""
    params = {"keyword": keyword, "subType": "HOTEL_LEISURE", "max": max_results}
    data = client.request("GET", "/v1/reference-data/locations/hotel", params=params)

    result = []
    for hotel in data.get("data", []):
        result.append({
            "hotel_id": hotel.get("hotelId"),
            "name": hotel.get("name"),
            "city": hotel.get("address", {}).get("cityName"),
            "country": hotel.get("address", {}).get("countryCode"),
            "location": hotel.get("geoCode"),
        })
    return result


def get_hotel_ratings(client: AmadeusClient, hotel_ids: str) -> list[dict]:
    """Get sentiment analysis ratings for hotels."""
    data = client.request(
        "GET", "/v2/e-reputation/hotel-sentiments", params={"hotelIds": hotel_ids}
    )
    result = []
    for hotel in data.get("data", []):
        result.append({
            "hotel_id": hotel.get("hotelId"),
            "overall_rating": hotel.get("overallRating"),
            "number_of_reviews": hotel.get("numberOfReviews"),
            "sentiment_scores": {
                k: hotel.get("sentimentScores", {}).get(k)
                for k in ["location", "comfort", "service", "staff", "internet", "food", "facilities"]
            },
        })
    return result


def book_hotel(
    client: AmadeusClient,
    offer_id: str,
    guests: list[dict],
    payment: dict,
) -> dict:
    """Book a hotel room."""
    request_body = {
        "data": {
            "offerId": offer_id,
            "guests": guests,
            "payments": [payment],
        }
    }
    data = client.request("POST", "/v1/booking/hotel-bookings", json_data=request_body)
    result = data.get("data", [{}])[0] if data.get("data") else {}
    return {
        "booking_id": result.get("id"),
        "provider_confirmation": result.get("providerConfirmationId"),
        "status": result.get("bookingStatus"),
    }
