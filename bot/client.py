"""Simple Binance Futures Testnet REST client."""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Any
from urllib.parse import urlencode

import requests

from .exceptions import BinanceAPIError, BinanceNetworkError

LOGGER = logging.getLogger(__name__)


class BinanceFuturesClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "https://testnet.binancefuture.com",
        timeout: int = 10,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret.encode("utf-8")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _sign(self, params: dict[str, Any]) -> str:
        query = urlencode(params, doseq=True)
        return hmac.new(
            self.api_secret, query.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    @staticmethod
    def _safe_params(params: dict[str, Any]) -> dict[str, Any]:
        data = dict(params)
        if "signature" in data:
            data["signature"] = "***"
        return data

    def signed_request(
        self, method: str, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        data = dict(params or {})
        data["timestamp"] = int(time.time() * 1000)
        data.setdefault("recvWindow", 5000)
        data["signature"] = self._sign(data)

        url = f"{self.base_url}{path}"
        headers = {"X-MBX-APIKEY": self.api_key}

        LOGGER.info(
            "API request | method=%s path=%s params=%s",
            method.upper(),
            path,
            self._safe_params(data),
        )

        try:
            res = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=data,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            LOGGER.exception("Network failure while calling Binance")
            raise BinanceNetworkError(str(exc)) from exc

        try:
            body = res.json()
        except ValueError as exc:
            LOGGER.error("Non-JSON response | status=%s body=%s", res.status_code, res.text)
            raise BinanceAPIError("Binance returned a non-JSON response.") from exc

        LOGGER.info("API response | status=%s body=%s", res.status_code, body)

        if res.status_code >= 400:
            msg = body.get("msg", "Unknown Binance API error")
            code = body.get("code", res.status_code)
            raise BinanceAPIError(f"Binance API error {code}: {msg}")

        return body

    def place_order(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.signed_request("POST", "/fapi/v1/order", params)
