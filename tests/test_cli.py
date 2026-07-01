"""Unit tests for CLI argument parsing (``cli.py``)."""

import pytest

from cli import build_parser


@pytest.fixture
def parser():
    """Return the argument parser instance."""
    return build_parser()


class TestArgparseConstruction:
    """Verify the parser is built correctly."""

    def test_parser_prog(self, parser) -> None:
        assert parser.prog == "trading-bot"

    def test_parser_has_all_arguments(self, parser) -> None:
        """All expected CLI flags are present."""
        seen = {a.dest for a in parser._actions}
        expected = {"symbol", "side", "order_type", "quantity",
                    "price", "ping", "verbose", "log_level", "version"}
        assert expected.issubset(seen), f"Missing: {expected - seen}"


class TestParsePing:
    """Tests for ``--ping`` flag."""

    def test_ping_flag(self, parser) -> None:
        args = parser.parse_args(["--ping"])
        assert args.ping is True
        assert args.symbol is None


class TestParseMarketOrder:
    """Tests for MARKET order arguments."""

    def test_minimal_market(self, parser) -> None:
        args = parser.parse_args([
            "--symbol", "BTCUSDT", "--side", "BUY",
            "--type", "MARKET", "--quantity", "0.01",
        ])
        assert args.symbol == "BTCUSDT"
        assert args.side == "BUY"
        assert args.order_type == "MARKET"
        assert args.quantity == 0.01
        assert args.price is None


class TestParseLimitOrder:
    """Tests for LIMIT order arguments."""

    def test_minimal_limit(self, parser) -> None:
        args = parser.parse_args([
            "--symbol", "ETHUSDT", "--side", "SELL",
            "--type", "LIMIT", "--quantity", "0.1", "--price", "3000",
        ])
        assert args.symbol == "ETHUSDT"
        assert args.side == "SELL"
        assert args.order_type == "LIMIT"
        assert args.quantity == 0.1
        assert args.price == 3000.0


class TestParseVerbose:
    """Tests for ``--verbose`` and ``--log-level``."""

    def test_verbose_flag(self, parser) -> None:
        args = parser.parse_args(["--verbose"])
        assert args.verbose is True

    def test_log_level(self, parser) -> None:
        args = parser.parse_args(["--log-level", "DEBUG"])
        assert args.log_level == "DEBUG"

    def test_log_level_case_insensitive(self, parser) -> None:
        args = parser.parse_args(["--log-level", "debug"])
        assert args.log_level == "DEBUG"

    def test_invalid_log_level(self, parser) -> None:
        with pytest.raises(SystemExit):
            parser.parse_args(["--log-level", "INVALID"])


class TestParseVersion:
    """Tests for ``--version`` flag."""

    def test_version_flag(self, parser) -> None:
        args = parser.parse_args(["--version"])
        assert args.version is True
