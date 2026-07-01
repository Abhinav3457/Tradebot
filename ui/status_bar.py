"""Status bar with connection indicator, execution timer, and clock."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import customtkinter as ctk

from ui.theme import (
    BG_CARD,
    FONT_SMALL,
    SUCCESS,
    DANGER,
    TEXT_SECONDARY,
    WARNING,
)


class StatusBar(ctk.CTkFrame):
    """Bottom status bar with connection indicator, execution timer, and clock."""

    def __init__(self, parent: Any, **kwargs: Any) -> None:
        super().__init__(parent, height=36, fg_color=BG_CARD, corner_radius=0, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Connection status (left)
        self.conn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.conn_frame.grid(row=0, column=0, sticky="w", padx=15, pady=6)

        self.conn_dot = ctk.CTkLabel(
            self.conn_frame, text="", width=10, height=10,
            fg_color=DANGER, corner_radius=5,
        )
        self.conn_dot.pack(side="left", padx=(0, 6))

        self.conn_label = ctk.CTkLabel(
            self.conn_frame, text="Disconnected",
            font=FONT_SMALL, text_color=TEXT_SECONDARY,
        )
        self.conn_label.pack(side="left")

        # Execution time (center)
        self.timer_label = ctk.CTkLabel(
            self, text="", font=FONT_SMALL, text_color=TEXT_SECONDARY,
        )
        self.timer_label.grid(row=0, column=1, sticky="")

        # Clock (right)
        self.clock_label = ctk.CTkLabel(
            self, text="", font=FONT_SMALL, text_color=TEXT_SECONDARY,
        )
        self.clock_label.grid(row=0, column=2, sticky="e", padx=15, pady=6)

        self._update_clock()

    def set_connected(self, connected: bool) -> None:
        if connected:
            self.conn_dot.configure(fg_color=SUCCESS)
            self.conn_label.configure(text="Connected", text_color=SUCCESS)
        else:
            self.conn_dot.configure(fg_color=DANGER)
            self.conn_label.configure(text="Disconnected", text_color=DANGER)

    def set_testnet(self) -> None:
        self.conn_dot.configure(fg_color=WARNING)
        self.conn_label.configure(text="Testnet", text_color=WARNING)

    def show_timer(self, seconds: float) -> None:
        self.timer_label.configure(text=f"Last order: {seconds:.2f}s")

    def clear_timer(self) -> None:
        self.timer_label.configure(text="")

    def _update_clock(self) -> None:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        self.clock_label.configure(text=now)
        self.after(1000, self._update_clock)
