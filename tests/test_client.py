"""Unit tests for the ``bot.client`` module with mocked Binance API."""

from unittest.mock import MagicMock, patch

import pytest

from bot.client import BinanceFuturesClient
from bot.exceptions import APIConnectionError, ConfigurationError, OrderPlacementError


@pytest.fixture
def client() -> BinanceFuturesClient:
    """Return a ``BinanceFuturesClient`` with test credentials."""
    return BinanceFuturesClient(
        api_key="test_key",
        api_secret="test_secret",
        testnet_url="https://testnet.binancefuture.com",
    )


class TestConnect:
    """Tests for ``BinanceFuturesClient.connect``."""

    @patch("bot.client.Client")
    def test_connect_success(self, mock_client_class: MagicMock, client: BinanceFuturesClient) -> None:
        """Connection succeeds with valid credentials."""
        client.connect()
        mock_client_class.assert_called_once_with(
            "test_key", "test_secret", testnet=True,
        )

    @patch("bot.client.Client", side_effect=Exception("Connection refused"))
    def test_connect_failure(self, mock_client_class: MagicMock, client: BinanceFuturesClient) -> None:
        """Connection failure raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Failed to initialise"):
            client.connect()


class TestTestConnection:
    """Tests for ``BinanceFuturesClient.test_connection``."""

    @patch("bot.client.Client")
    def test_ping_success(self, mock_client_class: MagicMock, client: BinanceFuturesClient) -> None:
        """Ping returns True on success."""
        client.connect()
        result = client.test_connection()
        assert result is True

    @patch("bot.client.Client")
    def test_ping_not_connected(self, mock_client_class: MagicMock, client: BinanceFuturesClient) -> None:
        """Ping without connect raises APIConnectionError."""
        with pytest.raises(APIConnectionError, match="Client not connected"):
            client.test_connection()


class TestMarketOrder:
    """Tests for ``BinanceFuturesClient.create_market_order``."""

    @patch("bot.client.Client")
    def test_market_order_success(self, mock_client_class: MagicMock, client: BinanceFuturesClient) -> None:
        """Market order returns expected response."""
        client.connect()
        mock_order = {"orderId": 123, "status": "FILLED", "executedQty": "0.01"}
        client._client.futures_create_order.return_value = mock_order

        result = client.create_market_order("BTCUSDT", "BUY", 0.01)
        assert result["orderId"] == 123
        assert result["status"] == "FILLED"
        client._client.futures_create_order.assert_called_once_with(
            symbol="BTCUSDT", side="BUY", type="MARKET", quantity=0.01,
        )


class TestLimitOrder:
    """Tests for ``BinanceFuturesClient.create_limit_order``."""

    @patch("bot.client.Client")
    def test_limit_order_success(self, mock_client_class: MagicMock, client: BinanceFuturesClient) -> None:
        """Limit order returns expected response."""
        client.connect()
        mock_order = {"orderId": 456, "status": "NEW", "executedQty": "0"}
        client._client.futures_create_order.return_value = mock_order

        result = client.create_limit_order("BTCUSDT", "SELL", 0.02, 105000.0)
        assert result["orderId"] == 456
        assert result["status"] == "NEW"
        client._client.futures_create_order.assert_called_once_with(
            symbol="BTCUSDT", side="SELL", type="LIMIT",
            timeInForce="GTC", quantity=0.02, price=105000.0,
        )
