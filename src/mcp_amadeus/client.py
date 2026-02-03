"""Amadeus Travel API client with OAuth token management."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Any, Optional

import httpx

from mcp_amadeus.config import get_settings


class AmadeusClient:
    """Sync/async Amadeus API client with automatic OAuth2 token refresh.

    Reads configuration from environment variables (AMADEUS_* prefix),
    .env file, or explicit constructor parameters.
    """

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        base_url: str | None = None,
    ) -> None:
        settings = get_settings()
        self.client_id = client_id or settings.client_id
        self.client_secret = client_secret or settings.client_secret
        self.base_url = base_url or settings.base_url
        self._access_token: str | None = None
        self._token_expiry: datetime | None = None

    # -- Token management -----------------------------------------------------

    def _get_token_sync(self) -> str:
        """Get or refresh OAuth access token (sync)."""
        if self._access_token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._access_token

        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/v1/security/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            data = response.json()

        self._access_token = data["access_token"]
        self._token_expiry = datetime.now() + timedelta(
            seconds=data.get("expires_in", 1700) - 60
        )
        return self._access_token

    async def _get_token_async(self) -> str:
        """Get or refresh OAuth access token (async)."""
        if self._access_token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._access_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/security/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            data = response.json()

        self._access_token = data["access_token"]
        self._token_expiry = datetime.now() + timedelta(
            seconds=data.get("expires_in", 1700) - 60
        )
        return self._access_token

    # -- Sync request ---------------------------------------------------------

    def request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        json_data: dict | None = None,
        timeout: float = 30.0,
    ) -> dict:
        """Make authenticated sync API request."""
        token = self._get_token_sync()
        with httpx.Client(timeout=timeout) as client:
            response = client.request(
                method,
                f"{self.base_url}{endpoint}",
                params=params,
                json=json_data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            if response.status_code == 204:
                return {}
            return response.json()

    def delete_request(
        self,
        endpoint: str,
        timeout: float = 30.0,
    ) -> dict:
        """Make authenticated DELETE request (handles 204 No Content)."""
        token = self._get_token_sync()
        with httpx.Client(timeout=timeout) as client:
            response = client.delete(
                f"{self.base_url}{endpoint}",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == 204:
                return {"status": "success"}
            response.raise_for_status()
            return response.json()

    # -- Async request --------------------------------------------------------

    async def arequest(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        json_data: dict | None = None,
        timeout: float = 30.0,
    ) -> dict:
        """Make authenticated async API request."""
        token = await self._get_token_async()
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method,
                f"{self.base_url}{endpoint}",
                params=params,
                json=json_data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            if response.status_code == 204:
                return {}
            return response.json()

    async def adelete_request(
        self,
        endpoint: str,
        timeout: float = 30.0,
    ) -> dict:
        """Make authenticated async DELETE request."""
        token = await self._get_token_async()
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.delete(
                f"{self.base_url}{endpoint}",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == 204:
                return {"status": "success"}
            response.raise_for_status()
            return response.json()
