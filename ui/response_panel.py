"""Order response display card with formatted fields."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import customtkinter as ctk

from ui.theme import (
    BG_CARD,
    BG_INPUT,
    FONT_BODY,
    FONT_SUBHEADER,
    PRIMARY,
    SUCCESS,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class ResponsePanel(ctk.CTkFrame):
    """Card that displays the formatted order response."""

    def __init__(self, parent: Any, **kwargs: Any) -> None:
        super().__init__(parent, fg_color=BG_CARD, corner_radius=10, **kwargs)

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Order Response", font=FONT_SUBHEADER,
            text_color=TEXT_PRIMARY, anchor="w",
        )
        self.title_label.pack(anchor="w", padx=15, pady=(12, 4))

        # Fields container
        self.fields_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.fields_frame.pack(fill="x", padx=15, pady=(0, 4))

        fields = [
            ("Order ID", "order_id"),
            ("Status", "status"),
            ("Executed Qty", "executed_qty"),
            ("Average Price", "avg_price"),
            ("Transaction Time", "trans_time"),
        ]

        self._field_labels: dict[str, ctk.CTkLabel] = {}
        for i, (label, key) in enumerate(fields):
            row_frame = ctk.CTkFrame(self.fields_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)

            ctk.CTkLabel(
                row_frame, text=f"{label}:",
                font=FONT_BODY, text_color=TEXT_SECONDARY, width=140, anchor="w",
            ).pack(side="left")

            value_label = ctk.CTkLabel(
                row_frame, text="--", font=FONT_BODY,
                text_color=TEXT_PRIMARY, anchor="w",
            )
            value_label.pack(side="left", fill="x", expand=True)
            self._field_labels[key] = value_label

        # Status separator
        self.separator = ctk.CTkFrame(self, height=1, fg_color=BG_INPUT)
        self.separator.pack(fill="x", padx=15, pady=6)

        # Status message
        self.status_message = ctk.CTkLabel(
            self, text="", font=FONT_SUBHEADER, text_color=SUCCESS,
        )
        self.status_message.pack(padx=15, pady=(0, 12))

        # Auto-clear timer
        self._clear_job: str | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def display_response(self, response: dict[str, Any]) -> None:
        """Populate the response fields from an order response dict."""
        self._field_labels["order_id"].configure(
            text=str(response.get("orderId", "N/A")),
        )
        self._field_labels["status"].configure(
            text=str(response.get("status", "N/A")),
        )
        self._field_labels["executed_qty"].configure(
            text=str(response.get("executedQty", "N/A")),
        )
        self._field_labels["avg_price"].configure(
            text=str(response.get("avgPrice", "N/A")),
        )

        ts = response.get("updateTime", 0)
        if ts:
            dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        else:
            time_str = "N/A"
        self._field_labels["trans_time"].configure(text=time_str)

        status = response.get("status", "UNKNOWN")
        if status in ("FILLED", "NEW", "PARTIALLY_FILLED"):
            self.status_message.configure(
                text=f"\u2705 Order Placed Successfully (Status: {status})",
                text_color=SUCCESS,
            )
        else:
            self.status_message.configure(
                text=f"Order Status: {status}",
                text_color=PRIMARY,
            )

        # Schedule auto-clear after 30 seconds
        if self._clear_job:
            self.after_cancel(self._clear_job)
        self._clear_job = self.after(30000, self.clear_display)

    def display_error(self, message: str) -> None:
        """Show an error message."""
        self.status_message.configure(
            text=f"\u274c {message}",
            text_color="#F44336",
        )

    def clear_display(self) -> None:
        """Reset all fields to defaults."""
        for key in self._field_labels:
            self._field_labels[key].configure(text="--")
        self.status_message.configure(text="")
