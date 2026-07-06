"""
Binance Futures API client wrapper.

Provides a clean interface for connecting to Binance Futures Testnet,
testing connectivity, and placing market/limit orders.

No CLI or user-interaction code lives here.
"""

from __future__ import annotations

from typing import Any

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.exceptions import APIConnectionError, OrderPlacementError, ConfigurationError
from bot.logger import setup_logger
from bot.utils import retry

logger = setup_logger(__name__)


class BinanceFuturesClient:
    """Thin wrapper around the ``binance.client.Client`` for Futures Testnet.

    Args:
        api_key: Binance API key.
        api_secret: Binance API secret.
        testnet_url: Base URL for Binance Futures Testnet.
    """

    def __init__(self, api_key: str, api_secret: str, testnet_url: str) -> None:
        self._api_key = api_key
        self._api_secret = api_secret
        self._testnet_url = testnet_url
        self._client: Client | None = None

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """Initialise the Binance client.

        Uses ``testnet=True`` to route to Binance Futures Testnet.
        The ``FUTURES_TESTNET_URL`` is automatically set to
        ``https://testnet.binancefuture.com/fapi`` by the library.

        If a custom ``TESTNET_URL`` is provided via config, it is used
        to override the default futures testnet URL.

        Raises:
            ConfigurationError: If client initialisation fails.
        """
        try:
            self._client = Client(
                self._api_key,
                self._api_secret,
                testnet=True,
            )
            # Allow override of the default testnet URL if configured
            if self._testnet_url != "https://testnet.binancefuture.com":
                self._client.FUTURES_TESTNET_URL = self._testnet_url
            logger.info(
                "Binance client initialised (testnet, url=%s)",
                self._client.FUTURES_TESTNET_URL,
            )
        except Exception as exc:
            logger.error("Failed to initialise Binance client: %s", exc)
            raise ConfigurationError(f"Failed to initialise Binance client: {exc}") from exc

    # ------------------------------------------------------------------
    # Connection test
    # ------------------------------------------------------------------

    def test_connection(self) -> bool:
        """Ping the Binance Futures Testnet to verify connectivity.

        Returns:
            ``True`` if the ping succeeds.

        Raises:
            APIConnectionError: If the ping fails (auth, network, etc.).
        """
        self._ensure_connected()
        try:
            self._client.futures_ping()  # type: ignore[union-attr]
            logger.info("Connection test (ping) successful")
            return True
        except BinanceAPIException as exc:
            logger.error("Binance API error during ping: %s", exc)
            raise APIConnectionError(
                f"Authentication failed. Check your API keys. ({exc.message})"
            ) from exc
        except BinanceRequestException as exc:
            logger.error("Network error during ping: %s", exc)
            raise APIConnectionError(
                f"Could not connect to Binance Testnet. ({exc.message})"
            ) from exc
        except Exception as exc:
            logger.error("Unexpected error during ping: %s", exc)
            raise APIConnectionError(f"Unexpected connection error: {exc}") from exc

    # ------------------------------------------------------------------
    # Orders
    # ------------------------------------------------------------------

    @retry(max_attempts=3)
    def create_market_order(
        self, symbol: str, side: str, quantity: float,
    ) -> dict[str, Any]:
        """Place a MARKET order on Binance Futures.

        Args:
            symbol: Trading pair, e.g. ``"BTCUSDT"``.
            side: ``"BUY"`` or ``"SELL"``.
            quantity: Order quantity.

        Returns:
            Raw API response dictionary.

        Raises:
            OrderPlacementError: On API or network failure.
        """
        self._ensure_connected()
        try:
            logger.info("MARKET %s %f %s", side, quantity, symbol)
            order: dict[str, Any] = self._client.futures_create_order(  # type: ignore[union-attr]
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=quantity,
            )
            logger.info("Market order response received: orderId=%s", order.get("orderId"))
            return order
        except BinanceAPIException as exc:
            logger.error("Binance API error (market): %s", exc)
            raise OrderPlacementError(f"Binance API error: {exc.message}") from exc
        except BinanceRequestException as exc:
            logger.error("Network error (market): %s", exc)
            raise OrderPlacementError(f"Network error: {exc.message}") from exc
        except Exception as exc:
            logger.error("Unexpected error (market): %s", exc)
            raise OrderPlacementError(f"Unexpected error: {exc}") from exc

    @retry(max_attempts=3)
    def create_limit_order(
        self, symbol: str, side: str, quantity: float, price: float,
        time_in_force: str = "GTC",
    ) -> dict[str, Any]:
        """Place a LIMIT order on Binance Futures.

        Args:
            symbol: Trading pair, e.g. ``"BTCUSDT"``.
            side: ``"BUY"`` or ``"SELL"``.
            quantity: Order quantity.
            price: Limit price.
            time_in_force: Time-in-force (default ``"GTC"``).

        Returns:
            Raw API response dictionary.

        Raises:
            OrderPlacementError: On API or network failure.
        """
        self._ensure_connected()
        try:
            logger.info("LIMIT %s %f %s @ %f", side, quantity, symbol, price)
            order: dict[str, Any] = self._client.futures_create_order(  # type: ignore[union-attr]
                symbol=symbol,
                side=side,
                type="LIMIT",
                timeInForce=time_in_force,
                quantity=quantity,
                price=price,
            )
            logger.info("Limit order response received: orderId=%s", order.get("orderId"))
            return order
        except BinanceAPIException as exc:
            logger.error("Binance API error (limit): %s", exc)
            raise OrderPlacementError(f"Binance API error: {exc.message}") from exc
        except BinanceRequestException as exc:
            logger.error("Network error (limit): %s", exc)
            raise OrderPlacementError(f"Network error: {exc.message}") from exc
        except Exception as exc:
            logger.error("Unexpected error (limit): %s", exc)
            raise OrderPlacementError(f"Unexpected error: {exc}") from exc

    # ------------------------------------------------------------------
    # Public accessor
    # ------------------------------------------------------------------

    @property
    def raw_client(self) -> Client | None:
        """Return the underlying ``binance.client.Client`` instance, or ``None``
        if ``connect()`` has not been called yet."""
        return self._client

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_connected(self) -> None:
        """Raise ``APIConnectionError`` if the client has not been connected."""
        if self._client is None:
            raise APIConnectionError(
                "Client not connected. Call connect() before using the client."
            )
