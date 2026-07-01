"""
Order business-logic layer.

Receives validated trading parameters, delegates to the API client,
and formats raw responses into clean, presentation-ready dictionaries.

No argparse or CLI code lives here.
"""

from __future__ import annotations

from typing import Any

from bot.client import BinanceFuturesClient
from bot.logger import setup_logger

logger = setup_logger(__name__)


class OrderService:
    """High-level service for placing trading orders.

    Args:
        client: An initialised ``BinanceFuturesClient`` instance.
    """

    def __init__(self, client: BinanceFuturesClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def place_market_order(
        self, symbol: str, side: str, quantity: float,
    ) -> dict[str, Any]:
        """Place a MARKET order.

        Args:
            symbol: Trading pair symbol.
            side: Order side (``"BUY"`` / ``"SELL"``).
            quantity: Order quantity.

        Returns:
            Formatted order response dictionary.
        """
        logger.info("Market order: %s %s %s qty=%s", symbol, side, "MARKET", quantity)
        raw = self._client.create_market_order(symbol, side, quantity)
        return self._format_response(raw)

    def place_limit_order(
        self, symbol: str, side: str, quantity: float, price: float,
    ) -> dict[str, Any]:
        """Place a LIMIT order.

        Args:
            symbol: Trading pair symbol.
            side: Order side (``"BUY"`` / ``"SELL"``).
            quantity: Order quantity.
            price: Limit price.

        Returns:
            Formatted order response dictionary.
        """
        logger.info("Limit order: %s %s %s qty=%s price=%s", symbol, side, "LIMIT", quantity, price)
        raw = self._client.create_limit_order(symbol, side, quantity, price)
        return self._format_response(raw)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_response(response: dict[str, Any]) -> dict[str, Any]:
        """Extract and normalise fields from the raw Binance API response."""
        return {
            "orderId": response.get("orderId"),
            "status": response.get("status"),
            "executedQty": response.get("executedQty"),
            "avgPrice": response.get("avgPrice"),
            "updateTime": response.get("updateTime"),
            "symbol": response.get("symbol"),
            "side": response.get("side"),
            "type": response.get("type"),
            "origQty": response.get("origQty"),
            "cumQuote": response.get("cumQuote"),
            "clientOrderId": response.get("clientOrderId"),
        }
