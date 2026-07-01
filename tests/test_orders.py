"""Unit tests for the ``bot.orders`` module."""

from unittest.mock import MagicMock

import pytest

from bot.orders import OrderService


@pytest.fixture
def mock_client() -> MagicMock:
    """Return a mocked BinanceFuturesClient."""
    client = MagicMock()
    client.create_market_order.return_value = {
        "orderId": 123,
        "status": "FILLED",
        "executedQty": "0.01",
        "avgPrice": "62450.00",
        "updateTime": 1720000000000,
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "origQty": "0.01",
        "cumQuote": "624.50",
        "clientOrderId": "test123",
    }
    client.create_limit_order.return_value = {
        "orderId": 456,
        "status": "NEW",
        "executedQty": "0",
        "avgPrice": "0",
        "updateTime": 1720000001000,
        "symbol": "BTCUSDT",
        "side": "SELL",
        "type": "LIMIT",
        "origQty": "0.02",
        "cumQuote": "0",
        "clientOrderId": "test456",
    }
    return client


@pytest.fixture
def service(mock_client: MagicMock) -> OrderService:
    """Return an OrderService with mocked client."""
    return OrderService(client=mock_client)


class TestPlaceMarketOrder:
    """Tests for ``OrderService.place_market_order``."""

    def test_returns_formatted_response(self, service: OrderService, mock_client: MagicMock) -> None:
        """Market order returns formatted dict with expected fields."""
        result = service.place_market_order("BTCUSDT", "BUY", 0.01)
        assert result["orderId"] == 123
        assert result["status"] == "FILLED"
        assert result["executedQty"] == "0.01"
        assert result["avgPrice"] == "62450.00"
        mock_client.create_market_order.assert_called_once_with("BTCUSDT", "BUY", 0.01)


class TestPlaceLimitOrder:
    """Tests for ``OrderService.place_limit_order``."""

    def test_returns_formatted_response(self, service: OrderService, mock_client: MagicMock) -> None:
        """Limit order returns formatted dict with expected fields."""
        result = service.place_limit_order("BTCUSDT", "SELL", 0.02, 105000.0)
        assert result["orderId"] == 456
        assert result["status"] == "NEW"
        assert result["executedQty"] == "0"
        mock_client.create_limit_order.assert_called_once_with("BTCUSDT", "SELL", 0.02, 105000.0)
