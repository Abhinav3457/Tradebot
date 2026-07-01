"""
Input validation for trading order parameters.

Every public function raises ``ValidationError`` (from
``bot.exceptions``) when a check fails.
"""

from decimal import Decimal, InvalidOperation
from typing import Any

from bot.exceptions import ValidationError

VALID_SIDES: frozenset[str] = frozenset({"BUY", "SELL"})
VALID_ORDER_TYPES: frozenset[str] = frozenset({"MARKET", "LIMIT"})


def validate_symbol(symbol: str) -> str:
    """Validate and normalise a trading pair symbol."""
    if not symbol or not symbol.strip():
        raise ValidationError("Symbol cannot be empty.")
    return symbol.strip().upper()


def validate_side(side: str) -> str:
    """Validate the order side (BUY / SELL)."""
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError(
            f"Side must be one of {{'BUY', 'SELL'}}, got {side!r}."
        )
    return s


def validate_order_type(order_type: str) -> str:
    """Validate the order type (MARKET / LIMIT)."""
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Order type must be one of {{'MARKET', 'LIMIT'}}, "
            f"got {order_type!r}."
        )
    return t


def validate_quantity(quantity: Any) -> float:
    """Validate that quantity is a positive number."""
    try:
        qty = float(Decimal(str(quantity)))
    except (ValueError, TypeError, InvalidOperation):
        raise ValidationError(
            f"Quantity must be a valid number, got {quantity!r}."
        )
    if qty <= 0:
        raise ValidationError(
            f"Quantity must be greater than zero, got {qty}."
        )
    return qty


def validate_price(price: Any) -> float:
    """Validate that price is a positive number."""
    try:
        p = float(Decimal(str(price)))
    except (ValueError, TypeError, InvalidOperation):
        raise ValidationError(
            f"Price must be a valid number, got {price!r}."
        )
    if p <= 0:
        raise ValidationError(
            f"Price must be greater than zero, got {p}."
        )
    return p
