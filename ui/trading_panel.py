"""Trading panel with order form and place-order button."""

from __future__ import annotations

from typing import Any, Callable

import customtkinter as ctk

from ui.theme import (
    BG_CARD,
    BG_INPUT,
    FONT_BODY,
    FONT_BUTTON,
    FONT_SUBHEADER,
    PRIMARY,
    PRIMARY_HOVER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT", "XRPUSDT"]


class TradingPanel(ctk.CTkFrame):
    """Left-side trading panel with order form controls."""

    def __init__(
        self, parent: Any,
        on_place_order: Callable[[dict[str, Any]], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, fg_color=BG_CARD, corner_radius=10, **kwargs)

        self._on_place_order = on_place_order
        self._executing = False

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Place Order", font=FONT_SUBHEADER,
            text_color=TEXT_PRIMARY, anchor="w",
        )
        self.title_label.pack(anchor="w", padx=15, pady=(12, 8))

        # --- Trading Pair --------------------------------------------------
        self._add_label("Trading Pair")
        self.symbol_var = ctk.StringVar(value=SYMBOLS[0])
        self.symbol_dropdown = ctk.CTkOptionMenu(
            self, values=SYMBOLS, variable=self.symbol_var,
            font=FONT_BODY, fg_color=BG_INPUT, button_color=PRIMARY,
            button_hover_color=PRIMARY_HOVER, dropdown_font=FONT_BODY,
        )
        self.symbol_dropdown.pack(fill="x", padx=15, pady=(0, 10))

        # --- Side (BUY/SELL) -----------------------------------------------
        self._add_label("Side")
        self.side_var = ctk.StringVar(value="BUY")
        self.side_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.side_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.buy_radio = ctk.CTkRadioButton(
            self.side_frame, text="BUY", variable=self.side_var,
            value="BUY", font=FONT_BODY, fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER, text_color="#4CAF50",
        )
        self.buy_radio.pack(side="left", padx=(0, 20))

        self.sell_radio = ctk.CTkRadioButton(
            self.side_frame, text="SELL", variable=self.side_var,
            value="SELL", font=FONT_BODY, fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER, text_color="#F44336",
        )
        self.sell_radio.pack(side="left")

        # --- Order Type (MARKET/LIMIT) -------------------------------------
        self._add_label("Order Type")
        self.type_var = ctk.StringVar(value="MARKET")
        self.type_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.type_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.market_radio = ctk.CTkRadioButton(
            self.type_frame, text="MARKET", variable=self.type_var,
            value="MARKET", font=FONT_BODY, fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER, command=self._on_type_change,
        )
        self.market_radio.pack(side="left", padx=(0, 20))

        self.limit_radio = ctk.CTkRadioButton(
            self.type_frame, text="LIMIT", variable=self.type_var,
            value="LIMIT", font=FONT_BODY, fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER, command=self._on_type_change,
        )
        self.limit_radio.pack(side="left")

        # --- Quantity ------------------------------------------------------
        self._add_label("Quantity")
        self.quantity_entry = ctk.CTkEntry(
            self, font=FONT_BODY, fg_color=BG_INPUT,
            border_color=PRIMARY, placeholder_text="e.g. 0.01",
        )
        self.quantity_entry.pack(fill="x", padx=15, pady=(0, 10))

        # --- Price ---------------------------------------------------------
        self._add_label("Price")
        self.price_entry = ctk.CTkEntry(
            self, font=FONT_BODY, fg_color=BG_INPUT,
            border_color=PRIMARY, placeholder_text="Required for LIMIT orders",
            state="disabled",
        )
        self.price_entry.pack(fill="x", padx=15, pady=(0, 16))

        # --- Place Order Button --------------------------------------------
        self.place_btn = ctk.CTkButton(
            self,
            text="PLACE ORDER",
            font=FONT_BUTTON,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            height=44,
            corner_radius=8,
            command=self._on_place_click,
        )
        self.place_btn.pack(fill="x", padx=15, pady=(0, 16))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_executing(self, executing: bool) -> None:
        """Enable or disable the place-order button during execution."""
        self._executing = executing
        if executing:
            self.place_btn.configure(
                text="PLACING ORDER...", state="disabled", fg_color="#555555",
            )
        else:
            self.place_btn.configure(
                text="PLACE ORDER", state="normal", fg_color=PRIMARY,
            )

    def get_order_data(self) -> dict[str, Any] | None:
        """Collect and return the form data as a dict, or None if invalid."""
        symbol = self.symbol_var.get()
        side = self.side_var.get()
        order_type = self.type_var.get()
        quantity = self.quantity_entry.get()
        price = self.price_entry.get()

        return {
            "symbol": symbol,
            "side": side,
            "order_type": order_type,
            "quantity": quantity,
            "price": price if price else None,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _add_label(self, text: str) -> None:
        ctk.CTkLabel(
            self, text=text, font=FONT_BODY,
            text_color=TEXT_SECONDARY, anchor="w",
        ).pack(anchor="w", padx=15, pady=(0, 3))

    def _on_type_change(self) -> None:
        """Enable/disable the price field based on order type."""
        if self.type_var.get() == "LIMIT":
            self.price_entry.configure(state="normal")
            self.price_entry.configure(placeholder_text="e.g. 50000")
        else:
            self.price_entry.configure(state="disabled")
            self.price_entry.configure(placeholder_text="Required for LIMIT orders")

    def _on_place_click(self) -> None:
        """Handle the place-order button click."""
        if self._executing:
            return
        if self._on_place_order:
            self._on_place_order(self.get_order_data())
