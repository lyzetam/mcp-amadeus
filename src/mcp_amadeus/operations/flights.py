"""Flight search, pricing, booking, and status operations."""

from __future__ import annotations

import json
from typing import Optional

from ..client import AmadeusClient


def search_flights(
    client: AmadeusClient,
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None = None,
    adults: int = 1,
    travel_class: str = "ECONOMY",
    nonstop: bool = False,
    max_results: int = 10,
) -> list[dict]:
    """Search for flight offers."""
    params = {
        "originLocationCode": origin.upper(),
        "destinationLocationCode": destination.upper(),
        "departureDate": departure_date,
        "adults": adults,
        "travelClass": travel_class,
        "nonStop": str(nonstop).lower(),
        "max": max_results,
        "currencyCode": "USD",
    }
    if return_date:
        params["returnDate"] = return_date

    data = client.request("GET", "/v2/shopping/flight-offers", params=params)

    result = []
    for offer in data.get("data", []):
        itineraries = []
        for itin in offer.get("itineraries", []):
            segments = []
            for seg in itin.get("segments", []):
                segments.append({
                    "departure": {
                        "airport": seg.get("departure", {}).get("iataCode"),
                        "time": seg.get("departure", {}).get("at"),
                    },
                    "arrival": {
                        "airport": seg.get("arrival", {}).get("iataCode"),
                        "time": seg.get("arrival", {}).get("at"),
                    },
                    "carrier": seg.get("carrierCode"),
                    "flight_number": seg.get("number"),
                    "duration": seg.get("duration"),
                })
            itineraries.append({
                "duration": itin.get("duration"),
                "segments": segments,
            })
        result.append({
            "id": offer.get("id"),
            "price": {
                "total": offer.get("price", {}).get("total"),
                "currency": offer.get("price", {}).get("currency"),
            },
            "itineraries": itineraries,
            "seats_available": offer.get("numberOfBookableSeats"),
        })
    return result


def get_flight_price(client: AmadeusClient, flight_offer: dict) -> dict:
    """Confirm price for a flight offer."""
    data = client.request(
        "POST",
        "/v1/shopping/flight-offers/pricing",
        json_data={"data": {"type": "flight-offers-pricing", "flightOffers": [flight_offer]}},
    )
    result = data.get("data", {})
    offers = result.get("flightOffers", [{}])
    return {
        "total_price": offers[0].get("price", {}).get("total") if offers else None,
        "price_breakdown": offers[0].get("travelerPricings", []) if offers else [],
    }


def search_flight_inspiration(
    client: AmadeusClient,
    origin: str,
    max_price: int | None = None,
    departure_date: str | None = None,
) -> list[dict]:
    """Get flight destination inspiration based on cheapest flights."""
    params = {"origin": origin.upper()}
    if max_price:
        params["maxPrice"] = max_price
    if departure_date:
        params["departureDate"] = departure_date

    data = client.request("GET", "/v1/shopping/flight-destinations", params=params)

    result = []
    for dest in data.get("data", [])[:20]:
        result.append({
            "destination": dest.get("destination"),
            "departure_date": dest.get("departureDate"),
            "return_date": dest.get("returnDate"),
            "price": dest.get("price", {}).get("total"),
        })
    return result


def search_flight_availability(
    client: AmadeusClient,
    origin: str,
    destination: str,
    departure_date: str,
    adults: int = 1,
) -> list[dict]:
    """Search for available seats on flights."""
    request_body = {
        "originDestinations": [{
            "id": "1",
            "originLocationCode": origin.upper(),
            "destinationLocationCode": destination.upper(),
            "departureDateTime": {"date": departure_date},
        }],
        "travelers": [{"id": str(i + 1), "travelerType": "ADULT"} for i in range(adults)],
        "sources": ["GDS"],
    }
    data = client.request("POST", "/v1/shopping/flight-availabilities", json_data=request_body)

    result = []
    for avail in data.get("data", [])[:10]:
        segments = []
        for seg in avail.get("segments", []):
            segments.append({
                "departure": seg.get("departure"),
                "arrival": seg.get("arrival"),
                "carrier": seg.get("carrierCode"),
                "flight_number": seg.get("number"),
                "aircraft": seg.get("aircraft", {}).get("code"),
                "available_classes": seg.get("availabilityClasses", []),
            })
        result.append({"id": avail.get("id"), "segments": segments})
    return result


def get_branded_fares(client: AmadeusClient, flight_offer: dict) -> list[dict]:
    """Get branded fare upsell options for a flight offer."""
    data = client.request(
        "POST",
        "/v1/shopping/flight-offers/upselling",
        json_data={"data": {"type": "flight-offers-upselling", "flightOffers": [flight_offer]}},
    )
    result = []
    for offer in data.get("data", []):
        fare_details = []
        pricings = offer.get("travelerPricings", [{}])
        for segment in pricings[0].get("fareDetailsBySegment", []) if pricings else []:
            fare_details.append({
                "segment_id": segment.get("segmentId"),
                "cabin": segment.get("cabin"),
                "fare_basis": segment.get("fareBasis"),
                "branded_fare": segment.get("brandedFare"),
                "included_bags": segment.get("includedCheckedBags"),
                "amenities": segment.get("amenities", []),
            })
        result.append({
            "offer_id": offer.get("id"),
            "price": offer.get("price"),
            "fare_details": fare_details,
        })
    return result


def get_seatmap(client: AmadeusClient, flight_offer: dict) -> list[dict]:
    """Get seatmap for a flight offer."""
    data = client.request("POST", "/v1/shopping/seatmaps", json_data={"data": [flight_offer]})

    result = []
    for seatmap in data.get("data", []):
        decks = []
        for deck in seatmap.get("decks", []):
            seats = []
            for seat in deck.get("seats", []):
                seats.append({
                    "number": seat.get("number"),
                    "cabin": seat.get("cabin"),
                    "available": seat.get("travelerPricing") is not None,
                    "characteristics": seat.get("characteristicsCodes", []),
                    "price": (
                        seat.get("travelerPricing", [{}])[0].get("price")
                        if seat.get("travelerPricing")
                        else None
                    ),
                })
            decks.append({
                "deck_type": deck.get("deckType"),
                "deck_configuration": deck.get("deckConfiguration"),
                "seats": seats[:50],
            })
        result.append({
            "flight_id": seatmap.get("flightOfferId"),
            "segment_id": seatmap.get("segmentId"),
            "aircraft": seatmap.get("aircraft"),
            "decks": decks,
        })
    return result


def get_flight_status(
    client: AmadeusClient,
    carrier_code: str,
    flight_number: str,
    departure_date: str,
) -> list[dict]:
    """Get real-time flight status information."""
    params = {
        "carrierCode": carrier_code.upper(),
        "flightNumber": flight_number,
        "scheduledDepartureDate": departure_date,
    }
    data = client.request("GET", "/v2/schedule/flights", params=params)

    result = []
    for flight in data.get("data", []):
        segments = flight.get("flightPoints", [])
        departure = segments[0] if segments else {}
        arrival = segments[-1] if len(segments) > 1 else {}
        result.append({
            "flight": f"{carrier_code.upper()}{flight_number}",
            "departure": {
                "airport": departure.get("iataCode"),
                "terminal": departure.get("departure", {}).get("terminal"),
                "scheduled": departure.get("departure", {}).get("at"),
            },
            "arrival": {
                "airport": arrival.get("iataCode"),
                "terminal": arrival.get("arrival", {}).get("terminal"),
                "scheduled": arrival.get("arrival", {}).get("at"),
            },
            "aircraft": flight.get("flightDesignator", {}).get("aircraftType"),
            "duration": flight.get("duration"),
        })
    return result
