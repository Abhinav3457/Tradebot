"""Unit tests for the bot.validators module."""

import pytest

from bot.exceptions import ValidationError
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)


class TestValidateSymbol:
    """Tests for validate_symbol."""

    def test_valid_symbol(self) -> None:
        assert validate_symbol("btcusdt") == "BTCUSDT"
        assert validate_symbol("ETHUSDT") == "ETHUSDT"

    def test_empty_symbol(self) -> None:
        with pytest.raises(ValidationError, match="Symbol cannot be empty"):
            validate_symbol("")

    def test_whitespace_only(self) -> None:
        with pytest.raises(ValidationError, match="Symbol cannot be empty"):
            validate_symbol("   ")


class TestValidateSide:
    """Tests for validate_side."""

    def test_valid_sides(self) -> None:
        assert validate_side("BUY") == "BUY"
        assert validate_side("sell") == "SELL"

    def test_invalid_side(self) -> None:
        with pytest.raises(ValidationError, match="Side must be one of"):
            validate_side("HOLD")


class TestValidateOrderType:
    """Tests for validate_order_type."""

    def test_valid_types(self) -> None:
        assert validate_order_type("MARKET") == "MARKET"
        assert validate_order_type("limit") == "LIMIT"

    def test_invalid_type(self) -> None:
        with pytest.raises(ValidationError, match="Order type must be one of"):
            validate_order_type("STOP")


class TestValidateQuantity:
    """Tests for validate_quantity."""

    def test_valid_quantities(self) -> None:
        assert validate_quantity(0.01) == 0.01
        assert validate_quantity("0.5") == 0.5

    def test_zero_quantity(self) -> None:
        with pytest.raises(ValidationError, match="Quantity must be greater than zero"):
            validate_quantity(0)

    def test_negative_quantity(self) -> None:
        with pytest.raises(ValidationError, match="Quantity must be greater than zero"):
            validate_quantity(-1)

    def test_non_numeric(self) -> None:
        with pytest.raises(ValidationError, match="Quantity must be a valid number"):
            validate_quantity("abc")


class TestValidatePrice:
    """Tests for validate_price."""

    def test_valid_prices(self) -> None:
        assert validate_price(50000.0) == 50000.0
        assert validate_price("105000") == 105000.0

    def test_zero_price(self) -> None:
        with pytest.raises(ValidationError, match="Price must be greater than zero"):
            validate_price(0)

    def test_negative_price(self) -> None:
        with pytest.raises(ValidationError, match="Price must be greater than zero"):
            validate_price(-100)

    def test_non_numeric_price(self) -> None:
        with pytest.raises(ValidationError, match="Price must be a valid number"):
            validate_price("free")
