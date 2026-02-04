# mcp-amadeus

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Amadeus Travel API as a Python library, LangChain tools, and MCP server. Search flights, book hotels, find activities, arrange transfers, and access travel analytics from code or an MCP-compatible client.

## Features

**38 tools** across 8 categories:

- **Flights** (7) -- search offers, confirm price, inspiration search, availability, branded fares, seatmaps, flight status
- **Hotels** (5) -- search by city, get details, search by name, ratings, book
- **Airports/Cities** (6) -- search airports, search cities, airport routes, nearest airports, airline destinations, on-time performance
- **Activities** (2) -- search tours/activities, get details
- **Transfers** (4) -- search ground transfers, book, get order, cancel
- **Analytics** (7) -- busiest travel period, most booked destinations, most traveled destinations, price analysis, delay prediction, choice prediction, trip purpose prediction
- **Orders** (3) -- create flight order, get order, cancel order
- **Misc** (4) -- travel recommendations, destination recommendations, parse trip document, get parsed trip

## Installation

```bash
# Core library only
pip install .

# With MCP server
pip install ".[mcp]"

# With LangChain tools
pip install ".[langchain]"

# Everything
pip install ".[all]"
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `AMADEUS_CLIENT_ID` | Amadeus API client ID | (required) |
| `AMADEUS_CLIENT_SECRET` | Amadeus API client secret | (required) |
| `AMADEUS_BASE_URL` | API base URL (test or production) | `https://test.api.amadeus.com` |

Create a `.env` file:

```env
AMADEUS_CLIENT_ID=your-client-id
AMADEUS_CLIENT_SECRET=your-client-secret
AMADEUS_BASE_URL=https://test.api.amadeus.com
```

Use `https://api.amadeus.com` for production access.

## Quick Start

### MCP Server

```bash
mcp-amadeus
```

### LangChain Tools

```python
from mcp_amadeus.langchain_tools import TOOLS, amadeus_search_flights

# Search for flights
result = amadeus_search_flights.invoke({
    "origin": "JFK",
    "destination": "LAX",
    "departure_date": "2025-03-15",
    "adults": 1,
})

# Or pass all tools to an agent
from langchain.agents import AgentExecutor
agent = AgentExecutor(tools=TOOLS, ...)
```

### Python Library

```python
from mcp_amadeus.client import AmadeusClient

client = AmadeusClient()

# Authenticated requests (OAuth2 handled automatically)
flights = client.get_sync("/v2/shopping/flight-offers", params={
    "originLocationCode": "JFK",
    "destinationLocationCode": "LAX",
    "departureDate": "2025-03-15",
    "adults": 1,
})
```

## License

MIT
