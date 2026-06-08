"""Application-specific exceptions."""


class TradingBotError(Exception):
    """Base exception for trading bot failures."""


class ValidationError(TradingBotError):
    """Raised when CLI input is invalid."""


class BinanceAPIError(TradingBotError):
    """Raised when Binance returns an error response."""


class BinanceNetworkError(TradingBotError):
    """Raised when a network request fails."""

