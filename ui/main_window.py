"""Main application window assembling all UI panels."""

from __future__ import annotations

import threading
import time
from typing import Any

import customtkinter as ctk

from ui.logs_panel import LogsPanel
from ui.response_panel import ResponsePanel
from ui.status_bar import StatusBar
from ui.theme import (
    BG_DARK,
    FONT_BODY,
    FONT_HEADER,
    FONT_SMALL,
    PRIMARY,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from ui.trading_panel import TradingPanel

VERSION = "1.0.0"


class MainWindow(ctk.CTk):
    """Main application window for the Binance Futures Trading Bot."""

    def __init__(
        self,
        on_ping: Any = None,
        on_place_order: Any = None,
    ) -> None:
        super().__init__()

        self._on_ping = on_ping
        self._on_place_order = on_place_order

        # Window configuration
        self.title("Binance Futures Trading Bot")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(fg_color=BG_DARK)

        # ---- Main Layout --------------------------------------------------
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        # ---- Header -------------------------------------------------------
        self._build_header()
        self._header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))

        # ---- Left Column: Trading Panel -----------------------------------
        self.trading_panel = TradingPanel(
            self,
            on_place_order=self._handle_place_order,
        )
        self.trading_panel.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=5)

        # ---- Right Column: Response + Logs --------------------------------
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)
        self.right_frame.grid_rowconfigure(0, weight=0)
        self.right_frame.grid_rowconfigure(1, weight=1)

        self.response_panel = ResponsePanel(self.right_frame)
        self.response_panel.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 5))

        self.logs_panel = LogsPanel(self.right_frame)
        self.logs_panel.grid(row=1, column=0, sticky="nsew", padx=0, pady=(5, 0))

        # ---- Status Bar ---------------------------------------------------
        self.grid_rowconfigure(2, weight=0)
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")

        # ---- Post-init ----------------------------------------------------
        self.logs_panel.log_info(f"Application started (v{VERSION})")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update_connection_status(self, connected: bool, testnet: bool = True) -> None:
        """Update the connection indicator in the header and status bar."""
        if connected:
            self.conn_status.configure(text="\U0001F7E2 Connected", text_color="#4CAF50")
        else:
            self.conn_status.configure(text="\U0001F534 Disconnected", text_color="#F44336")

        self.status_bar.set_connected(connected)
        if connected and testnet:
            self.status_bar.set_testnet()
            self.testnet_badge.configure(text="Testnet", fg_color="#FF9800")

    def show_order_response(self, response: dict[str, Any]) -> None:
        """Display an order response in the response panel."""
        self.response_panel.display_response(response)
        self.logs_panel.log_success(
            f"Order {response.get('orderId', '?')} - {response.get('status', 'UNKNOWN')}"
        )

    def show_error(self, message: str) -> None:
        """Display an error in the response panel and log."""
        self.response_panel.display_error(message)
        self.logs_panel.log_error(message)

    def log_message(self, message: str, level: str = "INFO") -> None:
        """Add a message to the live logs."""
        getattr(self.logs_panel, f"log_{level.lower()}", self.logs_panel.log_info)(message)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_header(self) -> None:
        """Build the top header bar."""
        self._header_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=10, height=60)

        self._header_frame.grid_columnconfigure(0, weight=1)
        self._header_frame.grid_columnconfigure(1, weight=0)
        self._header_frame.grid_columnconfigure(2, weight=1)

        # Title
        title_frame = ctk.CTkFrame(self._header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=12)

        ctk.CTkLabel(
            title_frame, text="Binance Futures Trading Bot",
            font=FONT_HEADER, text_color=TEXT_PRIMARY,
        ).pack(side="left")

        ctk.CTkLabel(
            title_frame, text=f"  v{VERSION}",
            font=FONT_SMALL, text_color=TEXT_SECONDARY,
        ).pack(side="left", padx=(4, 0))

        # Center: connection status + testnet badge
        center_frame = ctk.CTkFrame(self._header_frame, fg_color="transparent")
        center_frame.grid(row=0, column=1, sticky="", pady=12)

        self.conn_status = ctk.CTkLabel(
            center_frame, text="\U0001F534 Disconnected",
            font=FONT_BODY, text_color="#F44336",
        )
        self.conn_status.pack(side="left", padx=(0, 8))

        self.testnet_badge = ctk.CTkLabel(
            center_frame, text="Testnet",
            font=FONT_SMALL, fg_color="#555555",
            text_color="white", corner_radius=4, padx=8, pady=2,
        )
        self.testnet_badge.pack(side="left")

        # Right: ping button
        right_frame = ctk.CTkFrame(self._header_frame, fg_color="transparent")
        right_frame.grid(row=0, column=2, sticky="e", padx=20, pady=12)

        self.ping_btn = ctk.CTkButton(
            right_frame, text="Ping Binance", font=FONT_BODY,
            fg_color=PRIMARY, hover_color="#1565C0",
            height=30, width=110, command=self._handle_ping,
        )
        self.ping_btn.pack(side="right")

        about_btn = ctk.CTkButton(
            right_frame, text="About", font=FONT_BODY,
            fg_color="transparent", text_color=TEXT_SECONDARY,
            hover_color="#2A2A4A", height=30, width=60,
            command=self._show_about,
        )
        about_btn.pack(side="right", padx=(0, 8))

    def _handle_ping(self) -> None:
        """Handle the Ping button click."""
        if self._on_ping:
            self._on_ping(self)

    def _handle_place_order(self, order_data: dict[str, Any] | None) -> None:
        """Handle the place-order button click."""
        if order_data and self._on_place_order:
            self._on_place_order(self, order_data)

    def _show_about(self) -> None:
        """Show the About dialog."""
        about = ctk.CTkToplevel(self)
        about.title("About")
        about.geometry("350x200")
        about.resizable(False, False)
        about.transient(self)
        about.grab_set()

        ctk.CTkLabel(
            about, text="Binance Futures Trading Bot",
            font=("Segoe UI", 18, "bold"), text_color=TEXT_PRIMARY,
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            about, text=f"Version {VERSION}",
            font=FONT_BODY, text_color=TEXT_SECONDARY,
        ).pack(pady=5)

        ctk.CTkLabel(
            about, text="Binance Futures Testnet Desktop Client",
            font=FONT_BODY, text_color=TEXT_SECONDARY,
        ).pack(pady=5)

        ctk.CTkButton(
            about, text="Close", command=about.destroy,
            fg_color=PRIMARY, width=80,
        ).pack(pady=(15, 0))
