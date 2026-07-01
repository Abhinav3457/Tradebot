"""
Trading Bot — Binance Futures Testnet CLI.

A modular, production-quality application for placing futures orders
on the Binance Futures Testnet via a clean command-line interface.
"""

from bot.client import BinanceFuturesClient
from bot.config import Config, load_config
from bot.exceptions import (
    APIConnectionError,
    ConfigurationError,
    OrderPlacementError,
    ValidationError,
)
from bot.logger import setup_logger
from bot.orders import OrderService
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)

__all__ = [
    "BinanceFuturesClient",
    "Config",
    "load_config",
    "APIConnectionError",
    "ConfigurationError",
    "OrderPlacementError",
    "ValidationError",
    "setup_logger",
    "OrderService",
    "validate_order_type",
    "validate_price",
    "validate_quantity",
    "validate_side",
    "validate_symbol",
]
