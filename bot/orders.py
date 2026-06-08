"""Order helpers."""

from __future__ import annotations

import logging
from typing import Any

LOGGER = logging.getLogger(__name__)


class DryRunClient:
    def place_order(self, params: dict[str, Any]) -> dict[str, Any]:
        LOGGER.info("Dry-run order request | params=%s", params)
        return {
            "symbol": params["symbol"],
            "orderId": "DRY-RUN",
            "status": "DRY_RUN",
            "clientOrderId": "dry-run-client-order-id",
            "price": params.get("price", "0"),
            "avgPrice": "0",
            "origQty": params["quantity"],
            "executedQty": "0",
            "type": params["type"],
            "side": params["side"],
            "timeInForce": params.get("timeInForce"),
        }


def build_order_payload(order: dict[str, str]) -> dict[str, Any]:
    data: dict[str, Any] = {
        "symbol": order["symbol"],
        "side": order["side"],
        "type": "STOP" if order["order_type"] == "STOP_LIMIT" else order["order_type"],
        "quantity": order["quantity"],
        "newOrderRespType": "RESULT",
    }

    if order["order_type"] == "LIMIT":
        data["price"] = order["price"]
        data["timeInForce"] = "GTC"

    if order["order_type"] == "STOP_LIMIT":
        data["price"] = order["price"]
        data["stopPrice"] = order["stop_price"]
        data["timeInForce"] = "GTC"

    return data


def place_order(client: Any, order: dict[str, str]) -> dict[str, Any]:
    data = build_order_payload(order)
    LOGGER.info("Order placement started | summary=%s", order)
    res = client.place_order(data)
    LOGGER.info(
        "Order placement completed | orderId=%s status=%s executedQty=%s",
        res.get("orderId"),
        res.get("status"),
        res.get("executedQty"),
    )
    return res
