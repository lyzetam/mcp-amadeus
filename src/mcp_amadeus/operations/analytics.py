"""Flight analytics and prediction operations."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from ..client import AmadeusClient


def get_busiest_travel_period(
    client: AmadeusClient,
    city_code: str,
    year: str,
    direction: str = "ARRIVING",
) -> dict:
    """Get the busiest travel periods for a city."""
    params = {
        "cityCode": city_code.upper(),
        "period": year,
        "direction": direction.upper(),
    }
    data = client.request(
        "GET", "/v1/travel/analytics/air-traffic/busiest-period", params=params
    )

    periods = []
    for period in data.get("data", []):
        periods.append({
            "period": period.get("period"),
            "traveler_percentage": period.get("analytics", {}).get("travelers"),
        })
    return {
        "city": city_code.upper(),
        "year": year,
        "direction": direction,
        "periods": periods,
    }


def get_most_booked_destinations(
    client: AmadeusClient,
    origin_city: str,
    year: str,
    max_results: int = 20,
) -> dict:
    """Get most booked flight destinations from a city."""
    params = {
        "originCityCode": origin_city.upper(),
        "period": year,
        "max": max_results,
    }
    data = client.request(
        "GET", "/v1/travel/analytics/air-traffic/booked", params=params
    )

    destinations = []
    for dest in data.get("data", []):
        destinations.append({
            "destination": dest.get("destination"),
            "flights_score": dest.get("analytics", {}).get("flights"),
            "travelers_score": dest.get("analytics", {}).get("travelers"),
        })
    return {
        "origin": origin_city.upper(),
        "year": year,
        "destinations": destinations,
    }


def get_most_traveled_destinations(
    client: AmadeusClient,
    origin_city: str,
    year: str,
    max_results: int = 20,
) -> dict:
    """Get most traveled flight destinations from a city (by passenger volume)."""
    params = {
        "originCityCode": origin_city.upper(),
        "period": year,
        "max": max_results,
    }
    data = client.request(
        "GET", "/v1/travel/analytics/air-traffic/traveled", params=params
    )

    destinations = []
    for dest in data.get("data", []):
        destinations.append({
            "destination": dest.get("destination"),
            "flights_score": dest.get("analytics", {}).get("flights"),
            "travelers_score": dest.get("analytics", {}).get("travelers"),
        })
    return {
        "origin": origin_city.upper(),
        "year": year,
        "destinations": destinations,
    }


def analyze_flight_price(
    client: AmadeusClient,
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None = None,
) -> dict:
    """Analyze if a flight price is good compared to historical data."""
    params = {
        "originLocationCode": origin.upper(),
        "destinationLocationCode": destination.upper(),
        "departureDate": departure_date,
    }
    if return_date:
        params["returnDate"] = return_date

    data = client.request("GET", "/v1/analytics/flight-price-analysis", params=params)
    result = data.get("data", {})
    return {
        "route": f"{origin.upper()} -> {destination.upper()}",
        "departure_date": departure_date,
        "return_date": return_date,
        "average_price": result.get("analytics", {}).get("averagePrice"),
        "price_metrics": result.get("analytics"),
    }


def predict_flight_delay(
    client: AmadeusClient,
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
) -> dict:
    """Predict the probability of flight delay."""
    params = {
        "originLocationCode": origin.upper(),
        "destinationLocationCode": destination.upper(),
        "departureDate": departure_date,
        "departureTime": departure_time,
        "arrivalDate": arrival_date,
        "arrivalTime": arrival_time,
        "carrierCode": carrier_code.upper(),
        "flightNumber": flight_number,
        "aircraftCode": aircraft_code,
        "duration": duration,
    }
    data = client.request("GET", "/v1/travel/predictions/flight-delay", params=params)
    result = data.get("data", {})
    return {
        "flight": f"{carrier_code.upper()}{flight_number}",
        "route": f"{origin.upper()} -> {destination.upper()}",
        "prediction_result": result.get("result"),
        "delay_probabilities": result.get("probability"),
    }


def predict_flight_choice(client: AmadeusClient, flight_offers: list) -> list[dict]:
    """Predict which flight offer travelers are most likely to choose."""
    data = client.request(
        "POST",
        "/v1/shopping/flight-offers/prediction",
        json_data={
            "data": {"type": "flight-offers-prediction", "flightOffers": flight_offers}
        },
    )
    predictions = []
    for offer in data.get("data", []):
        predictions.append({
            "offer_id": offer.get("id"),
            "choice_probability": offer.get("choicePrediction", {}).get("score"),
            "prediction_factors": offer.get("choicePrediction", {}).get("predictionFactors"),
        })
    return predictions


def predict_trip_purpose(
    client: AmadeusClient,
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str,
    search_date: str | None = None,
) -> dict:
    """Predict if a trip is for business or leisure."""
    if not search_date:
        search_date = datetime.now().strftime("%Y-%m-%d")

    params = {
        "originLocationCode": origin.upper(),
        "destinationLocationCode": destination.upper(),
        "departureDate": departure_date,
        "returnDate": return_date,
        "searchDate": search_date,
    }
    data = client.request("GET", "/v1/travel/trip-purpose-predictions", params=params)
    result = data.get("data", {})
    return {
        "route": f"{origin.upper()} -> {destination.upper()}",
        "dates": f"{departure_date} to {return_date}",
        "predicted_purpose": result.get("result"),
        "business_probability": result.get("probabilities", {}).get("BUSINESS"),
        "leisure_probability": result.get("probabilities", {}).get("LEISURE"),
    }
