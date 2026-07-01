"""
Custom exception classes for the trading bot application.

Each exception type maps to a distinct failure mode, enabling
precise error handling and user-friendly messaging at every layer.
"""


class ValidationError(Exception):
    """Raised when user-supplied input fails validation checks.

    Examples: empty symbol, zero quantity, invalid order side.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"Validation Error: {self.message}"


class APIConnectionError(Exception):
    """Raised when the application cannot connect to or authenticate
    with the Binance Futures Testnet API.

    Examples: wrong API keys, network timeout, DNS resolution failure.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"API Connection Error: {self.message}"


class OrderPlacementError(Exception):
    """Raised when an order submission is rejected by the exchange or
    fails due to a network/API error.

    Examples: insufficient balance, invalid lot size, exchange rejection.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"Order Placement Error: {self.message}"


class ConfigurationError(Exception):
    """Raised when the application configuration is invalid or incomplete.

    Examples: missing API_KEY in .env, malformed environment variable.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"Configuration Error: {self.message}"
