"""UI theme configuration for CustomTkinter trading bot application.

Defines colors, fonts, and styling constants used across all UI panels.
"""

import customtkinter as ctk

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------

PRIMARY = "#1E88E5"  # Blue accent
PRIMARY_HOVER = "#1565C0"
PRIMARY_DARK = "#0D47A1"
SUCCESS = "#4CAF50"
DANGER = "#F44336"
WARNING = "#FF9800"
BG_DARK = "#1a1a2e"
BG_CARD = "#16213e"
BG_INPUT = "#0f3460"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#B0B0B0"
BORDER = "#2A2A4A"

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

FONT_FAMILY = "Segoe UI"

FONT_HEADER = (FONT_FAMILY, 22, "bold")
FONT_SUBHEADER = (FONT_FAMILY, 14, "bold")
FONT_BODY = (FONT_FAMILY, 13)
FONT_SMALL = (FONT_FAMILY, 11)
FONT_BUTTON = (FONT_FAMILY, 14, "bold")
FONT_MONO = ("Consolas", 12)

# ---------------------------------------------------------------------------
# Theme configuration for CustomTkinter
# ---------------------------------------------------------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ---------------------------------------------------------------------------
# Color helper functions
# ---------------------------------------------------------------------------


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert a hex color string to an RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
