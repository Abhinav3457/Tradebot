"""Live logs panel with scrollable text display."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import customtkinter as ctk

from ui.theme import (
    BG_CARD,
    BG_INPUT,
    FONT_MONO,
    FONT_SUBHEADER,
    PRIMARY,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class LogsPanel(ctk.CTkFrame):
    """Scrollable log output panel that displays application events."""

    def __init__(self, parent: Any, **kwargs: Any) -> None:
        super().__init__(parent, fg_color=BG_CARD, corner_radius=10, **kwargs)

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Live Logs", font=FONT_SUBHEADER,
            text_color=TEXT_PRIMARY, anchor="w",
        )
        self.title_label.pack(anchor="w", padx=15, pady=(12, 4))

        # Log text box
        self.log_box = ctk.CTkTextbox(
            self,
            font=FONT_MONO,
            fg_color=BG_INPUT,
            text_color=TEXT_SECONDARY,
            corner_radius=8,
            wrap="word",
            height=150,
        )
        self.log_box.pack(fill="both", expand=True, padx=15, pady=(0, 12))

        # Buttons row
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=15, pady=(0, 12))

        self.clear_btn = ctk.CTkButton(
            self.btn_frame, text="Clear Logs", font=FONT_MONO,
            fg_color="transparent", text_color=TEXT_SECONDARY,
            hover_color=BG_INPUT, border_width=1, border_color=TEXT_SECONDARY,
            width=100, height=28, command=self.clear_logs,
        )
        self.clear_btn.pack(side="right")

        # Configure log-level colour tags (called once for performance)
        self.log_box.tag_config("INFO", foreground=TEXT_SECONDARY)
        self.log_box.tag_config("WARNING", foreground="#FF9800")
        self.log_box.tag_config("ERROR", foreground="#F44336")
        self.log_box.tag_config("SUCCESS", foreground="#4CAF50")
        self.log_box.tag_config("DEBUG", foreground="#90CAF9")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log(self, message: str, level: str = "INFO") -> None:
        """Append a timestamped log entry to the display."""
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        tag = level.upper()

        color_map = {
            "INFO": TEXT_SECONDARY,
            "WARNING": "#FF9800",
            "ERROR": "#F44336",
            "SUCCESS": "#4CAF50",
            "DEBUG": "#90CAF9",
        }
        color = color_map.get(tag, TEXT_SECONDARY)

        line = f"[{timestamp}] [{tag}] {message}\n"
        self.log_box.insert("end", line)
        self.log_box.see("end")
        self.log_box.tag_config(tag, foreground=color)

    def log_info(self, message: str) -> None:
        self.log(message, "INFO")

    def log_success(self, message: str) -> None:
        self.log(message, "SUCCESS")

    def log_warning(self, message: str) -> None:
        self.log(message, "WARNING")

    def log_error(self, message: str) -> None:
        self.log(message, "ERROR")

    def clear_logs(self) -> None:
        self.log_box.delete("1.0", "end")
