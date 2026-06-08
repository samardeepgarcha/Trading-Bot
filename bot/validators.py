"""Validation helpers for command line input."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from .exceptions import ValidationError

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


def normalize_symbol(symbol: str) -> str:
    value = symbol.strip().upper()
    if not SYMBOL_PATTERN.fullmatch(value):
        raise ValidationError(
            "Symbol must be 5-20 uppercase letters/numbers, for example BTCUSDT."
        )
    return value


def normalize_side(side: str) -> str:
    value = side.strip().upper()
    if value not in VALID_SIDES:
        raise ValidationError("Side must be BUY or SELL.")
    return value


def normalize_order_type(order_type: str) -> str:
    value = order_type.strip().upper().replace("-", "_")
    if value not in VALID_ORDER_TYPES:
        raise ValidationError("Order type must be MARKET, LIMIT, or STOP_LIMIT.")
    return value


def positive_decimal(value: str, field_name: str) -> str:
    try:
        num = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"{field_name} must be a positive number.") from exc

    if num <= 0:
        raise ValidationError(f"{field_name} must be greater than zero.")
    return format(num.normalize(), "f")


def validate_order_args(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
    stop_price: str | None = None,
) -> dict[str, str]:
    order = {
        "symbol": normalize_symbol(symbol),
        "side": normalize_side(side),
        "order_type": normalize_order_type(order_type),
        "quantity": positive_decimal(quantity, "Quantity"),
    }

    if order["order_type"] in {"LIMIT", "STOP_LIMIT"}:
        if price is None:
            raise ValidationError("Price is required for LIMIT and STOP_LIMIT orders.")
        order["price"] = positive_decimal(price, "Price")
    elif price is not None:
        raise ValidationError("Price is only valid for LIMIT and STOP_LIMIT orders.")

    if order["order_type"] == "STOP_LIMIT":
        if stop_price is None:
            raise ValidationError("Stop price is required for STOP_LIMIT orders.")
        order["stop_price"] = positive_decimal(stop_price, "Stop price")
    elif stop_price is not None:
        raise ValidationError("Stop price is only valid for STOP_LIMIT orders.")

    return order
