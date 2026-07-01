"""
Configuration module responsible for loading and validating
environment variables from a .env file.

Reads:
    API_KEY      -- Binance Futures Testnet API key
    API_SECRET   -- Binance Futures Testnet API secret
    TESTNET_URL  -- Binance Futures Testnet base URL (with fallback)
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from bot.exceptions import ConfigurationError


@dataclass(frozen=True, slots=True)
class Config:
    """Immutable configuration container for Binance API credentials."""

    api_key: str
    api_secret: str
    testnet_url: str


ENV_PATH: Path = Path(__file__).resolve().parent.parent / ".env"


def load_config(env_file: str | Path = ENV_PATH) -> Config:
    """Load and validate configuration from a .env file.

    Args:
        env_file: Path to the .env file. Defaults to ``.env`` at the
            project root.

    Returns:
        A validated ``Config`` dataclass instance.

    Raises:
        ConfigurationError: If ``API_KEY`` or ``API_SECRET`` are missing
            or empty.
    """
    load_dotenv(dotenv_path=Path(env_file), override=True)

    api_key = os.getenv("API_KEY", "").strip()
    api_secret = os.getenv("API_SECRET", "").strip()
    testnet_url = os.getenv(
        "TESTNET_URL",
        "https://testnet.binancefuture.com",
    ).strip()

    if not api_key:
        raise ConfigurationError(
            "API_KEY is missing. "
            "Add it to your .env file or check the API_KEY variable name."
        )
    if not api_secret:
        raise ConfigurationError(
            "API_SECRET is missing. "
            "Add it to your .env file or check the API_SECRET variable name."
        )

    testnet_url = testnet_url.rstrip("/")

    return Config(
        api_key=api_key,
        api_secret=api_secret,
        testnet_url=testnet_url,
    )
