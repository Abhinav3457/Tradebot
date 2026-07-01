"""
Flask web dashboard for the Binance Futures Trading Bot.

Reuses the existing ``bot/`` backend - no business logic is duplicated.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add project root to sys.path so bot/ package is importable
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from flask import Flask, jsonify, render_template, request

from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.client import BinanceFuturesClient
from bot.config import load_config
from bot.exceptions import (
    APIConnectionError,
    ConfigurationError,
    OrderPlacementError,
    ValidationError,
)
from bot.logger import setup_logger
from bot.orders import OrderService
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)

logger = setup_logger(__name__)

app = Flask(__name__)

_client: BinanceFuturesClient | None = None
_order_service: OrderService | None = None


# ------------------------------------------------------------------
# Helper to ensure backend is initialised
# ------------------------------------------------------------------
def _require_client() -> BinanceFuturesClient:
    if _client is None:
        raise RuntimeError("Backend not initialised")
    return _client


def init_backend() -> str | None:
    """Initialise the Binance client and order service."""
    global _client, _order_service
    try:
        config = load_config()
        _client = BinanceFuturesClient(
            config.api_key, config.api_secret, config.testnet_url,
        )
        _client.connect()
        _order_service = OrderService(_client)
        logger.info("Web backend initialised successfully")
        return None
    except ConfigurationError as exc:
        logger.error("Web backend init failed: %s", exc)
        return str(exc)


@app.route("/")
def index():
    """Serve the main dashboard page."""
    status = "connected" if _client is not None else "disconnected"
    return render_template("index.html", status=status)


@app.route("/api/ping", methods=["GET"])
def api_ping():
    """Test API connectivity."""
    start = time.perf_counter()
    if _client is None:
        return jsonify({"success": False, "error": "Backend not initialised"}), 503
    try:
        _client.test_connection()
        elapsed = round(time.perf_counter() - start, 3)
        return jsonify({
            "success": True,
            "message": "Binance Futures Testnet is reachable",
            "elapsed": elapsed,
        })
    except APIConnectionError as exc:
        elapsed = round(time.perf_counter() - start, 3)
        return jsonify({"success": False, "error": str(exc), "elapsed": elapsed}), 502
    except Exception as exc:
        elapsed = round(time.perf_counter() - start, 3)
        return jsonify({"success": False, "error": f"Unexpected error: {exc}", "elapsed": elapsed}), 500


@app.route("/api/order", methods=["POST"])
def api_place_order():
    """Place a trading order."""
    if _order_service is None:
        return jsonify({"success": False, "error": "Backend not initialised"}), 503

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON body"}), 400

    start = time.perf_counter()

    try:
        symbol = validate_symbol(data.get("symbol", ""))
        side = validate_side(data.get("side", ""))
        order_type = validate_order_type(data.get("type", ""))
        quantity = validate_quantity(data.get("quantity", 0))

        price = None
        if order_type == "LIMIT":
            price_raw = data.get("price")
            if not price_raw:
                raise ValidationError("Price is required for LIMIT orders.")
            price = validate_price(price_raw)

        if order_type == "MARKET":
            response = _order_service.place_market_order(symbol, side, quantity)
        else:
            response = _order_service.place_limit_order(symbol, side, quantity, price)

        elapsed = time.perf_counter() - start

        return jsonify({
            "success": True,
            "elapsed": round(elapsed, 3),
            "order": {
                "orderId": response.get("orderId"),
                "status": response.get("status"),
                "executedQty": response.get("executedQty"),
                "avgPrice": response.get("avgPrice"),
                "symbol": response.get("symbol"),
                "side": response.get("side"),
                "type": response.get("type"),
            },
        })

    except (ValidationError, APIConnectionError, OrderPlacementError) as exc:
        elapsed = time.perf_counter() - start
        return jsonify({
            "success": False,
            "error": str(exc),
            "elapsed": round(elapsed, 3),
        }), 400
    except Exception as exc:
        elapsed = time.perf_counter() - start
        logger.exception("Web order unexpected error: %s", exc)
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {exc}",
            "elapsed": round(elapsed, 3),
        }), 500


# ------------------------------------------------------------------
# Public API endpoints
# ------------------------------------------------------------------


@app.route("/api/ticker/<symbol>", methods=["GET"])
def api_ticker(symbol):
    """Get 24-hour ticker data for a symbol."""
    try:
        client = _require_client()
        client.test_connection()  # verify connectivity first
        raw_client = getattr(client, "_client", None)
        if raw_client is None:
            return jsonify({"success": False, "error": "Binance client not connected"}), 503
        raw = raw_client.futures_ticker(symbol=symbol.upper())
        return jsonify({
            "success": True,
            "ticker": {
                "symbol": raw.get("symbol"),
                "lastPrice": raw.get("lastPrice"),
                "priceChange": raw.get("priceChange"),
                "priceChangePercent": raw.get("priceChangePercent"),
                "highPrice": raw.get("highPrice"),
                "lowPrice": raw.get("lowPrice"),
                "volume": raw.get("volume"),
                "quoteVolume": raw.get("quoteVolume"),
                "count": raw.get("count"),
                "markPrice": raw.get("markPrice"),
            },
        })
    except RuntimeError as exc:
        return jsonify({"success": False, "error": str(exc)}), 503
    except APIConnectionError as exc:
        return jsonify({"success": False, "error": str(exc)}), 502
    except BinanceAPIException as exc:
        return jsonify({"success": False, "error": f"Binance API error: {exc.message}"}), 502
    except BinanceRequestException as exc:
        return jsonify({"success": False, "error": f"Network error: {exc.message}"}), 502
    except Exception as exc:
        logger.exception("Ticker error: %s", exc)
        return jsonify({"success": False, "error": f"Unexpected error: {exc}"}), 500


@app.route("/api/account", methods=["GET"])
def api_account():
    """Get futures account overview."""
    try:
        client = _require_client()
        client.test_connection()  # verify connectivity first
        raw_client = getattr(client, "_client", None)
        if raw_client is None:
            return jsonify({"success": False, "error": "Binance client not connected"}), 503
        raw = raw_client.futures_account()

        # Normalise positions list
        positions = [
            {
                "symbol": p.get("symbol"),
                "positionAmt": p.get("positionAmt"),
                "entryPrice": p.get("entryPrice"),
                "markPrice": p.get("markPrice"),
                "unRealizedProfit": p.get("unRealizedProfit"),
                "leverage": p.get("leverage"),
            }
            for p in (raw.get("positions") or [])
        ]

        return jsonify({
            "success": True,
            "account": {
                "totalWalletBalance": raw.get("totalWalletBalance"),
                "totalUnrealizedProfit": raw.get("totalUnrealizedProfit"),
                "availableBalance": raw.get("availableBalance"),
                "maxWithdrawAmount": raw.get("maxWithdrawAmount"),
                "positions": positions,
            },
        })
    except RuntimeError as exc:
        return jsonify({"success": False, "error": str(exc)}), 503
    except APIConnectionError as exc:
        return jsonify({"success": False, "error": str(exc)}), 502
    except BinanceAPIException as exc:
        return jsonify({"success": False, "error": f"Binance API error: {exc.message}"}), 502
    except BinanceRequestException as exc:
        return jsonify({"success": False, "error": f"Network error: {exc.message}"}), 502
    except Exception as exc:
        logger.exception("Account error: %s", exc)
        return jsonify({"success": False, "error": f"Unexpected error: {exc}"}), 500


# Initialise backend on import so gunicorn workers have the client available
err = init_backend()
if err:
    logger.error("Web backend init failed: %s", err)
    print(f"ERROR: {err}")
    print("The web app will start but the backend is unavailable.")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
