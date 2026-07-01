"""
Desktop GUI entry point for the Binance Futures Trading Bot.

Initialises the backend (config, client, order service), then launches
the CustomTkinter main window. All order placement is delegated to the
existing backend — no business logic is duplicated.
"""

from __future__ import annotations

import sys
import threading
import time
from typing import Any

from bot.client import BinanceFuturesClient
from bot.config import load_config
from bot.exceptions import (
    APIConnectionError,
    ConfigurationError,
    OrderPlacementError,
    ValidationError,
)
from bot.logger import setup_logger
from bot.orders import OrderService
import customtkinter as ctk

from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)
from ui.main_window import MainWindow

logger = setup_logger(__name__)


class TradingBotApp:
    """Application controller that wires the backend to the GUI.

    Args:
        config_path: Optional path to the .env file.
    """

    def __init__(self, config_path: str | None = None) -> None:
        self._config_path = config_path
        self._client: BinanceFuturesClient | None = None
        self._order_service: OrderService | None = None
        self._window: MainWindow | None = None

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def initialise(self) -> None:
        """Load config, connect to Binance, and report status."""
        try:
            config = load_config()
            self._client = BinanceFuturesClient(
                config.api_key, config.api_secret, config.testnet_url,
            )
            self._client.connect()
            self._order_service = OrderService(self._client)
            logger.info("Backend initialised successfully")
        except ConfigurationError as exc:
            logger.error("Initialisation failed: %s", exc)
            raise

    def launch(self) -> None:
        """Create the main window and start the GUI event loop."""
        self._window = MainWindow(
            on_ping=self._handle_ping,
            on_place_order=self._handle_place_order,
        )
        self._window.update_connection_status(connected=True, testnet=True)
        self._window.log_message("Backend connected to Binance Futures Testnet")

        # Show initial connection status
        self._window.after(500, self._initial_ping)

        self._window.mainloop()

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _initial_ping(self) -> None:
        """Run a quick connection test on startup asynchronously."""
        def _ping() -> None:
            try:
                self._client.test_connection()  # type: ignore[union-attr]
                self._window.after(0, lambda: self._window.log_message(
                    "Connection test: Binance Futures Testnet reachable", "success",
                ))
            except Exception as exc:
                msg = str(exc)
                self._window.after(0, lambda m=msg: self._window.log_message(
                    f"Initial ping failed: {m}", "error",
                ))
        threading.Thread(target=_ping, daemon=True).start()



    def _show_success_popup(self, message: str) -> None:
        """Show a success popup dialog."""
        popup = ctk.CTkToplevel(self._window)
        popup.title("Success")
        popup.geometry("320x160")
        popup.resizable(False, False)
        popup.transient(self._window)
        popup.grab_set()
        ctk.CTkLabel(popup, text="✅", font=("Segoe UI", 40), text_color="#4CAF50").pack(pady=(20, 5))
        ctk.CTkLabel(popup, text=message, font=("Segoe UI", 14, "bold"), text_color="#FFFFFF", wraplength=280).pack(pady=5)
        ctk.CTkButton(popup, text="OK", command=popup.destroy, fg_color="#1E88E5", width=80).pack(pady=(10, 0))

    def _show_error_popup(self, message: str) -> None:
        """Show an error popup dialog."""
        popup = ctk.CTkToplevel(self._window)
        popup.title("Error")
        popup.geometry("320x180")
        popup.resizable(False, False)
        popup.transient(self._window)
        popup.grab_set()
        ctk.CTkLabel(popup, text="❌", font=("Segoe UI", 40), text_color="#F44336").pack(pady=(20, 5))
        ctk.CTkLabel(popup, text=message, font=("Segoe UI", 13), text_color="#FFFFFF", wraplength=280).pack(pady=5)
        ctk.CTkButton(popup, text="OK", command=popup.destroy, fg_color="#F44336", width=80).pack(pady=(10, 0))
    def _handle_ping(self, window: MainWindow) -> None:
        """Handle the Ping button from the GUI."""
        def _do_ping() -> None:
            window.ping_btn.configure(text="Pinging...", state="disabled")
            try:
                self._client.test_connection()  # type: ignore[union-attr]
                window.after(0, lambda: self._show_ping_result(window, True))
            except APIConnectionError as exc:
                msg = str(exc)
                window.after(0, lambda m=msg: self._show_ping_result(window, False, m))
            except Exception as exc:
                msg = str(exc)
                window.after(0, lambda m=msg: self._show_ping_result(window, False, m))

        threading.Thread(target=_do_ping, daemon=True).start()

    def _show_ping_result(self, window: MainWindow, success: bool, message: str = "") -> None:
        """Display the ping result in the GUI."""
        window.ping_btn.configure(text="Ping Binance", state="normal")
        if success:
            window.log_message("Ping successful - Binance Futures Testnet is reachable", "success")
        else:
            window.log_message(f"Ping failed: {message}", "error")
            window.show_error(f"Ping failed: {message}")

    def _handle_place_order(self, window: MainWindow, order_data: dict[str, Any]) -> None:
        """Handle order placement from the GUI.

        Validates inputs using the backend validators, then delegates
        to the order service.
        """
        window.trading_panel.set_executing(True)
        window.log_message(
            f"Processing order: {order_data['side']} {order_data['order_type']} "
            f"{order_data['quantity']} {order_data['symbol']}",
        )

        def _execute() -> None:
            start = time.perf_counter()
            try:
                # ---- Validate using backend validators --------------------
                symbol = validate_symbol(order_data["symbol"])
                side = validate_side(order_data["side"])
                order_type = validate_order_type(order_data["order_type"])
                quantity = validate_quantity(order_data["quantity"])

                price = None
                if order_type == "LIMIT":
                    if not order_data.get("price"):
                        raise ValidationError("Price is required for LIMIT orders.")
                    price = validate_price(order_data["price"])

                # ---- Place order via backend ------------------------------
                if order_type == "MARKET":
                    response = self._order_service.place_market_order(  # type: ignore[union-attr]
                        symbol, side, quantity,
                    )
                else:
                    response = self._order_service.place_limit_order(  # type: ignore[union-attr]
                        symbol, side, quantity, price,
                    )

                elapsed = time.perf_counter() - start

                # ---- Update GUI on main thread ----------------------------
                window.after(0, lambda: self._order_success(window, response, elapsed))

            except (ValidationError, APIConnectionError, OrderPlacementError) as exc:
                elapsed = time.perf_counter() - start
                msg = str(exc)
                window.after(0, lambda m=msg, e=elapsed: self._order_error(window, m, e))
            except Exception as exc:
                elapsed = time.perf_counter() - start
                logger.exception("Unexpected order error: %s", exc)
                msg = f"Unexpected error: {exc}"
                window.after(0, lambda m=msg, e=elapsed: self._order_error(
                    window, m, e,
                ))

        threading.Thread(target=_execute, daemon=True).start()

    def _order_success(self, window: MainWindow, response: dict[str, Any], elapsed: float) -> None:
        """Update GUI on successful order."""
        window.trading_panel.set_executing(False)
        window.show_order_response(response)
        window.status_bar.show_timer(elapsed)
        window.log_message(
            f"Order completed in {elapsed:.2f}s - "
            f"ID={response.get('orderId')} Status={response.get('status')}",
            "success",
        )

    def _order_error(self, window: MainWindow, message: str, elapsed: float) -> None:
        """Update GUI on order error."""
        window.trading_panel.set_executing(False)
        window.show_error(message)
        window.status_bar.show_timer(elapsed)
        window.log_message(f"Order failed: {message}", "error")


def main() -> None:
    """Application entry point."""
    app = TradingBotApp()

    try:
        app.initialise()
    except ConfigurationError as exc:
        print(f"ERROR: {exc}")
        print("Check your .env file and API keys.")
        sys.exit(1)

    app.launch()


if __name__ == "__main__":
    main()
