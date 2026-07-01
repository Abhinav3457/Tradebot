"""
Utility functions for terminal output formatting, execution timing,
date conversion, and a retry decorator.

No business logic lives here — only reusable helpers.
"""

from __future__ import annotations

import contextlib
import functools
import time
from datetime import datetime, timezone
from typing import Any, Callable, ParamSpec, TypeVar

from rich.console import Console
from rich.table import Table
from rich import box
from halo import Halo

from bot.exceptions import APIConnectionError, OrderPlacementError
from bot.logger import setup_logger

console = Console()
logger = setup_logger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def print_banner() -> None:
    """Display the ASCII project banner in cyan."""
    line = "=" * 47
    banner = f"\n{line}\n"
    banner += "      BINANCE FUTURES TRADING BOT      \n"
    banner += "          Testnet Mode Active          \n"
    banner += line
    console.print(banner, style="bold cyan")


def print_order_request(
    symbol: str, side: str, order_type: str, quantity: float, price: float | None = None,
) -> None:
    """Print a formatted order-request summary table."""
    table = Table(box=box.ROUNDED, title="ORDER REQUEST", title_style="bold yellow")
    table.add_column("Parameter", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Symbol", symbol)
    table.add_row("Side", side)
    table.add_row("Type", order_type)
    table.add_row("Quantity", str(quantity))
    if price is not None:
        table.add_row("Price", str(price))
    console.print()
    console.print(table)
    console.print()


def print_order_response(response: dict[str, Any]) -> None:
    """Print a formatted order-response table."""
    table = Table(box=box.ROUNDED, title="ORDER RESPONSE", title_style="bold yellow")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Order ID", str(response.get("orderId", "N/A")))
    table.add_row("Status", str(response.get("status", "N/A")))
    table.add_row("Executed Qty", str(response.get("executedQty", "N/A")))
    table.add_row("Average Price", str(response.get("avgPrice", "N/A")))
    table.add_row("Transaction Time", _format_timestamp(response.get("updateTime", 0)))
    console.print(table)
    console.print()


def print_success(message: str) -> None:
    """Print a green success message."""
    console.print(f"[bold green]OK: {message}[/bold green]\n")


def print_error(message: str) -> None:
    """Print a red error message."""
    console.print(f"[bold red]ERROR: {message}[/bold red]\n")


def print_info(message: str) -> None:
    """Print a blue informational message."""
    console.print(f"[bold blue]i[/bold blue] {message}\n")


def print_warning(message: str) -> None:
    """Print a yellow warning message."""
    console.print(f"[bold yellow]WARNING: {message}[/bold yellow]\n")


def print_separator() -> None:
    """Print a horizontal separator line."""
    console.print("=" * 50, style="dim")


def _format_timestamp(ts: int) -> str:
    """Convert a millisecond Unix timestamp to a human-readable string."""
    if not ts:
        return "N/A"
    dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


class ExecutionTimer:
    """Context manager that prints elapsed time on exit."""

    def __enter__(self) -> ExecutionTimer:
        self._start: float = time.perf_counter()
        return self

    def __exit__(self, *_: Any) -> None:
        elapsed: float = time.perf_counter() - self._start
        console.print(f"[dim]Execution Time: {elapsed:.2f}s[/dim]\n")


@contextlib.contextmanager
def spinner(text: str = "Sending order to Binance Futures Testnet..."):
    """Show a Halo spinner while a blocking operation runs."""
    spin = Halo(text=text, spinner="dots", color="cyan")
    spin.start()
    try:
        yield
    finally:
        spin.stop()


def retry(
    max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator that retries a function on transient failures."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exception: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except (APIConnectionError, OrderPlacementError) as exc:
                    last_exception = exc
                    if attempt < max_attempts:
                        wait = delay * (backoff ** (attempt - 1))
                        logger.warning(
                            "Attempt %d/%d failed. Retrying in %.1fs...",
                            attempt, max_attempts, wait,
                        )
                        print_warning(
                            f"Attempt {attempt}/{max_attempts} failed. "
                            f"Retrying in {wait:.1f}s..."
                        )
                        time.sleep(wait)
            if last_exception:
                raise last_exception
            raise RuntimeError("Unreachable")
        return wrapper
    return decorator
