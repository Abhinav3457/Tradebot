"""
Application entry point.

Uses ``argparse`` to parse CLI arguments, validates them, delegates to
the order service, and displays cleanly formatted output to the user.
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import NoReturn

from bot.client import BinanceFuturesClient
from bot.config import load_config
from bot.exceptions import (
    APIConnectionError,
    ConfigurationError,
    OrderPlacementError,
    ValidationError,
)
from bot.logger import LOG_LEVELS, setup_logger
from bot.orders import OrderService
from bot.utils import (
    ExecutionTimer,
    print_banner,
    print_error,
    print_info,
    print_order_request,
    print_order_response,
    print_separator,
    print_success,
    spinner,
)
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)

__version__ = "1.0.0"

logger = setup_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser.

    Returns:
        Configured ``ArgumentParser`` instance.
    """
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description="Binance Futures Testnet CLI Trading Bot",
        epilog=(
            "Examples:\n"
            "  python cli.py --ping\n"
            "  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01\n"
            "  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.02 --price 105000\n"
            "  python cli.py --version"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--symbol",
        type=str,
        metavar="PAIR",
        help="Trading pair symbol (e.g., BTCUSDT, ETHUSDT)",
    )
    parser.add_argument(
        "--side",
        type=str,
        choices=["BUY", "SELL"],
        metavar="{BUY,SELL}",
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["MARKET", "LIMIT"],
        dest="order_type",
        metavar="{MARKET,LIMIT}",
        help="Order type: MARKET or LIMIT",
    )
    parser.add_argument(
        "--quantity",
        type=float,
        metavar="AMOUNT",
        help="Order quantity (must be > 0)",
    )
    parser.add_argument(
        "--price",
        type=float,
        default=None,
        metavar="PRICE",
        help="Limit price in USDT (required for LIMIT orders)",
    )
    parser.add_argument(
        "--ping",
        action="store_true",
        help="Test API connectivity to Binance Futures Testnet",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output (DEBUG-level console logging)",
    )
    parser.add_argument(
        "--log-level",
        type=str.upper,
        choices=LOG_LEVELS,
        default=None,
        metavar="LEVEL",
        help="Set logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show program version and exit",
    )

    return parser


def handle_ping(client: BinanceFuturesClient) -> None:
    """Test API connectivity and display the result."""
    print_info("Testing connection to Binance Futures Testnet...")
    with spinner("Pinging Binance Futures Testnet..."):
        client.test_connection()
    print_success("Connection successful! Binance Futures Testnet is reachable.")
    logger.info("Ping command completed successfully")


def handle_order(args: argparse.Namespace, order_service: OrderService) -> None:
    """Validate arguments and place an order.

    Args:
        args: Parsed CLI arguments.
        order_service: Initialised ``OrderService`` instance.
    """
    # --- Validate ---------------------------------------------------------
    symbol = validate_symbol(args.symbol)
    side = validate_side(args.side)
    order_type = validate_order_type(args.order_type)
    quantity = validate_quantity(args.quantity)

    price: float | None = None
    if order_type == "LIMIT":
        if args.price is None:
            raise ValidationError("Price is required for LIMIT orders. Use --price.")
        price = validate_price(args.price)

    # --- Display request --------------------------------------------------
    print_banner()
    print_order_request(symbol, side, order_type, quantity, price)
    print_separator()

    # --- Confirm order (bonus) --------------------------------------------
    _confirm_order(symbol, side, order_type, quantity, price)

    # --- Place order ------------------------------------------------------
    with spinner("Sending order to Binance Futures Testnet..."):
        with ExecutionTimer():
            if order_type == "MARKET":
                response = order_service.place_market_order(symbol, side, quantity)
            else:
                response = order_service.place_limit_order(symbol, side, quantity, price)

    # --- Display response -------------------------------------------------
    print_separator()
    print_order_response(response)
    print_separator()

    status = response.get("status", "UNKNOWN")
    if status in ("FILLED", "NEW", "PARTIALLY_FILLED"):
        print_success(f"Order Placed Successfully (Status: {status})")
    else:
        print_info(f"Order Status: {status}")

    logger.info(
        "Order completed: symbol=%s side=%s type=%s qty=%s status=%s orderId=%s",
        symbol, side, order_type, quantity, status, response.get("orderId"),
    )


def _confirm_order(
    symbol: str, side: str, order_type: str, quantity: float, price: float | None,
) -> None:
    """Prompt the user to confirm the order before sending.

    Skips confirmation in non-interactive mode (piped input).
    """
    if not sys.stdin.isatty():
        return

    price_str = f" @ {price}" if price is not None else ""
    prompt = (
        f"Confirm {side} {order_type} {quantity} {symbol}{price_str}? "
        f"[y/N]: "
    )
    try:
        answer = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = "n"

    if answer not in ("y", "yes"):
        print_info("Order cancelled by user.")
        logger.info("User cancelled order")
        sys.exit(0)


def main() -> NoReturn:
    """Application entry point.

    Parses CLI arguments, loads configuration, initialises the client,
    and dispatches to the appropriate handler (ping or order).

    Exits with code 0 on success, 1 on any error.
    """
    parser = build_parser()
    args = parser.parse_args()

    # --- Handle --version early -------------------------------------------
    if args.version:
        print_info(f"trading-bot version {__version__}")
        logger.info("Version query: %s", __version__)
        sys.exit(0)

    # --- Configure logging level ------------------------------------------
    if args.verbose:
        _set_console_level(logging.DEBUG)
    if args.log_level:
        _set_console_level(getattr(logging, args.log_level))

    # --- Print banner upfront (always) ------------------------------------
    print_banner()

    # --- Load configuration -----------------------------------------------
    try:
        config = load_config()
    except ConfigurationError as exc:
        print_error(str(exc))
        logger.error("Configuration error: %s", exc)
        sys.exit(1)

    # --- Initialise client ------------------------------------------------
    try:
        client = BinanceFuturesClient(config.api_key, config.api_secret, config.testnet_url)
        client.connect()
    except ConfigurationError as exc:
        print_error(str(exc))
        logger.error("Client initialisation error: %s", exc)
        sys.exit(1)

    # --- Handle --ping flag -----------------------------------------------
    if args.ping:
        try:
            handle_ping(client)
        except APIConnectionError as exc:
            print_error(str(exc))
            logger.error("Ping failed: %s", exc)
            sys.exit(1)
        sys.exit(0)

    # --- Validate required arguments for orders ---------------------------
    required = ["symbol", "side", "order_type", "quantity"]
    missing = [r for r in required if getattr(args, r, None) is None]
    if missing:
        print_error(
            f"Missing required arguments: {', '.join(missing)}. "
            f"Use --help for usage information."
        )
        sys.exit(1)

    # --- Place order ------------------------------------------------------
    order_service = OrderService(client)

    try:
        handle_order(args, order_service)
    except ValidationError as exc:
        print_error(str(exc))
        logger.error("Validation error: %s", exc)
        sys.exit(1)
    except (APIConnectionError, OrderPlacementError) as exc:
        print_error(str(exc))
        logger.error("Order failed: %s", exc)
        sys.exit(1)
    except KeyboardInterrupt:
        print_info("Interrupted by user.")
        logger.info("KeyboardInterrupt received, shutting down gracefully.")
        sys.exit(0)
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        print_error("An unexpected error occurred. Check logs/app.log for details.")
        sys.exit(1)

    sys.exit(0)


def _set_console_level(level: int) -> None:
    """Dynamically adjust the console handler log level."""
    root = logging.getLogger("trading_bot")
    for handler in root.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setLevel(level)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_info("\nInterrupted by user. Exiting.")
        sys.exit(0)
