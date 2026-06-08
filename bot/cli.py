"""CLI for placing testnet orders."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from .client import BinanceFuturesClient
from .exceptions import BinanceAPIError, BinanceNetworkError, ValidationError
from .logging_config import configure_logging
from .orders import DryRunClient, place_order
from .validators import validate_order_args


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place Binance Futures Testnet orders from the command line."
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, for example BTCUSDT.")
    parser.add_argument("--side", required=True, help="BUY or SELL.")
    parser.add_argument(
        "--type",
        required=True,
        dest="order_type",
        help="MARKET, LIMIT, or STOP_LIMIT.",
    )
    parser.add_argument("--quantity", required=True, help="Order quantity.")
    parser.add_argument("--price", help="Required for LIMIT and STOP_LIMIT orders.")
    parser.add_argument("--stop-price", help="Required for STOP_LIMIT orders.")
    parser.add_argument(
        "--base-url",
        default=os.getenv("BINANCE_BASE_URL", "https://testnet.binancefuture.com"),
        help="Binance Futures API base URL.",
    )
    parser.add_argument(
        "--log-file",
        default="logs/trading_bot.log",
        help="Path where API requests, responses, and errors are logged.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and log the order without sending it to Binance.",
    )
    return parser


def print_order_summary(order: dict[str, str], dry_run: bool) -> None:
    print("\nOrder request summary")
    print("---------------------")
    print(f"Mode       : {'DRY RUN' if dry_run else 'LIVE TESTNET'}")
    print(f"Symbol     : {order['symbol']}")
    print(f"Side       : {order['side']}")
    print(f"Type       : {order['order_type']}")
    print(f"Quantity   : {order['quantity']}")
    if "price" in order:
        print(f"Price      : {order['price']}")
    if "stop_price" in order:
        print(f"Stop price : {order['stop_price']}")


def print_order_response(response: dict[str, Any]) -> None:
    print("\nOrder response details")
    print("----------------------")
    print(f"Order ID     : {response.get('orderId', 'N/A')}")
    print(f"Status       : {response.get('status', 'N/A')}")
    print(f"Executed Qty : {response.get('executedQty', 'N/A')}")
    print(f"Avg Price    : {response.get('avgPrice', response.get('price', 'N/A'))}")
    print(f"Client ID    : {response.get('clientOrderId', 'N/A')}")


def make_client(args: argparse.Namespace):
    if args.dry_run:
        return DryRunClient()

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        raise ValidationError(
            "Set BINANCE_API_KEY and BINANCE_API_SECRET, or use --dry-run."
        )

    return BinanceFuturesClient(
        api_key=api_key,
        api_secret=api_secret,
        base_url=args.base_url,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.log_file)

    try:
        order = validate_order_args(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
        print_order_summary(order, args.dry_run)
        res = place_order(make_client(args), order)
        print_order_response(res)
        print("\nSuccess: order submitted." if not args.dry_run else "\nSuccess: dry run completed.")
        return 0
    except ValidationError as exc:
        print(f"Validation error: {exc}", file=sys.stderr)
    except BinanceAPIError as exc:
        print(f"API error: {exc}", file=sys.stderr)
    except BinanceNetworkError as exc:
        print(f"Network error: {exc}", file=sys.stderr)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
