# Trading Bot — Binance Futures Testnet CLI

A production-quality, CLI-based trading bot that connects to **Binance Futures Testnet** and places futures orders using simulated funds. Built with clean architecture, modular design, and professional-grade error handling.

---

## Features

### Multiple Interfaces
- 🖥️ **CLI** — Full-featured command-line interface with rich terminal output
- 🖼️ **Desktop GUI** — CustomTkinter-based desktop application
- 🌐 **Web Dashboard** — Flask-powered responsive web dashboard with live market data

### Core
- 🔐 **Secure API Key Management** — Load credentials from `.env` file, never hardcoded
- 📦 **Market & Limit Orders** — Support for both `MARKET` and `LIMIT` order types
- 🔄 **Buy & Sell Support** — Place orders on both sides of the market
- ✅ **Input Validation** — Every parameter validated with `Decimal` precision before reaching the API
- 🛡️ **Graceful Error Handling** — Meaningful messages for every failure mode; no raw tracebacks
- 📝 **Comprehensive Logging** — Rotating file handler (5 MB, 3 backups) with structured log entries
- ⏳ **Loading Spinner** — Visual feedback while waiting for API responses (`halo`)
- 🔄 **Retry Logic** — Automatic retry (up to 3 attempts) with exponential backoff on transient failures
- ⏱️ **Execution Timer** — Track how long each order takes
- 📊 **Rich Terminal Output** — Formatted tables with `rich`, colored messages
- ✅ **Connection Test** — `--ping` flag to verify API connectivity
- 🏷️ **Version Display** — `--version` flag
- 🔉 **Verbose Mode** — `--verbose` and `--log-level` for granular logging control
- ⌨️ **Keyboard Interrupt** — Graceful `Ctrl+C` handling

---

## Architecture

```
                    +-----------+
                    |   User    |
                    +-----+-----+
                          |
          +---------------+---------------+
          |               |               |
    +-----v-----+  +-----v------+  +-----v------+
    | cli.py    |  | main.py    |  | web/app.py |
    | (CLI)     |  | (Desktop   |  | (Web       |
    | argparse  |  |  GUI)      |  |  Dashboard)|
    +-----+-----+  +-----+------+  +-----+------+
          |               |               |
          +-------+-------+-------+-------+
                  |               |
           +------v------+     +--v-----------+
           | validators  |     | orders.py    |
           | (validation)|     | (business    |
           +------+------+     | logic layer) |
                  |            +------+-------+
                  |                   |
                  |            +------v------+
                  |            | client.py   |  BinanceFuturesClient
                  |            | (@retry)    |  (wraps python-binance)
                  |            +------+------+
                  |                   |
                  |            +------v------+
                  |            | python-     |
                  |            | binance     |  HTTPS → testnet.binancefuture.com
                  |            +------+------+
                  |                   |
                  |            +------v------+
                  |            | Binance     |
                  +----+------+ Futures      |
                       |      | Testnet API  |
                       |      +-------------+
                  +----v----+
                  | config  |  Loads .env → API_KEY, API_SECRET, TESTNET_URL
                  +---------+
```

### Data Flow (CLI Example)

```
1. User runs: python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
2. cli.py parses args via argparse
3. config.py loads API credentials from .env
4. client.py initializes BinanceFuturesClient (testnet=True)
5. validators.py validates symbol, side, type, quantity
6. User confirms order (interactive prompt)
7. orders.py formats the request and delegates to client
8. client.py calls Binance Futures API via python-binance
9. On transient failure: @retry decorator retries up to 3x
10. Response is formatted and displayed as a rich table
11. All activity is logged to logs/app.log
```

---

## Project Structure

```
trading-bot/
│
├── bot/                          # Core application package (shared across all UIs)
│   ├── __init__.py               # Package initializer, re-exports public API
│   ├── client.py                 # Binance API client wrapper (@retry on orders)
│   ├── config.py                 # Environment variable loader (frozen dataclass)
│   ├── exceptions.py             # 4 custom exception classes
│   ├── logger.py                 # RotatingFileHandler (5MB, 3 backups)
│   ├── orders.py                 # OrderService business logic layer
│   ├── utils.py                  # rich tables, halo spinner, retry decorator, timer
│   └── validators.py             # Input validation (Decimal precision)
│
├── cli.py                        # CLI entry point (argparse)
├── main.py                       # Desktop GUI entry point (customtkinter)
├── web/                          # Web dashboard (Flask)
│   ├── __init__.py
│   ├── app.py                    # Flask routes & API endpoints
│   ├── templates/
│   │   └── index.html            # Dashboard HTML template
│   └── static/
│       ├── style.css             # Responsive dashboard styles
│       └── script.js             # Interactive dashboard logic
│
├── ui/                           # Desktop GUI components (customtkinter)
│   ├── __init__.py
│   ├── main_window.py
│   ├── trading_panel.py
│   ├── response_panel.py
│   ├── logs_panel.py
│   ├── status_bar.py
│   └── theme.py
│
├── tests/                        # Unit test suite (pytest)
│   ├── __init__.py
│   ├── test_validators.py        # Validation edge cases
│   ├── test_client.py            # Mocked Binance API → connect, ping, orders
│   ├── test_orders.py            # OrderService formatting and delegation
│   └── test_cli.py               # Argparse parsing for all flags
│
├── CHANGELOG.md                  # Version history
├── CONTRIBUTING.md               # Contribution guidelines
├── LICENSE                       # MIT License
├── README.md                     # This file
├── .gitignore
└── requirements.txt              # Python dependencies
```

---

## Installation

### Prerequisites

- Python **3.10+**
- Binance Futures Testnet account
- `pip` package manager

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd trading-bot
```

### Step 2: Create a Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Test Dependencies (optional)

```bash
pip install pytest pytest-mock
```

### Step 5: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your Binance Futures Testnet API keys:

```ini
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
TESTNET_URL=https://testnet.binancefuture.com
```

### Step 6: Generate Binance Testnet API Keys

1. Go to [Binance Futures Testnet](https://testnet.binancefuture.com/)
2. Log in or create a testnet account
3. Navigate to **API Management**
4. Generate a new API key
5. Copy the **API Key** and **Secret Key** into your `.env` file
6. The testnet provides **3000 USDT** of fake funds by default

> ⚠️ **Never share your API keys** or commit the `.env` file to version control.

---

## Usage

### 💻 CLI Interface

```bash
# Test API connection
python cli.py --ping

# Place a MARKET Buy order
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

# Place a LIMIT Sell order
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.02 --price 105000

# Check version
python cli.py --version
```

### 🖼️ Desktop GUI

```bash
python main.py
```

### 🌐 Web Dashboard

```bash
python web/app.py
```

Then open **http://127.0.0.1:5000** in your browser. The dashboard features:
- Live market data (price, 24h change, volume) with auto-refresh
- Account overview (balance, PnL, open positions)
- Place MARKET and LIMIT orders
- Activity log with timestamps
- Light/dark theme toggle
- Fully responsive (desktop, tablet, mobile)

---

## CLI Arguments

| Argument        | Required                 | Description                                   |
|----------------|--------------------------|-----------------------------------------------|
| `--symbol`     | Yes (orders)             | Trading pair symbol (e.g., BTCUSDT, ETHUSDT)  |
| `--side`       | Yes (orders)             | Order side: `BUY` or `SELL`                   |
| `--type`       | Yes (orders)             | Order type: `MARKET` or `LIMIT`               |
| `--quantity`   | Yes (orders)             | Order quantity (must be > 0)                  |
| `--price`      | Yes (for LIMIT)          | Limit price in USDT                           |
| `--ping`       | No                       | Test API connectivity (standalone)            |
| `--verbose`    | No                       | Enable DEBUG-level console logging            |
| `--log-level`  | No                       | Set specific log level (DEBUG/INFO/WARNING/ERROR) |
| `--version`    | No                       | Show program version and exit                 |
| `--help`       | No                       | Show help message and exit                    |

---

## Output Example

```
===============================================
      BINANCE FUTURES TRADING BOT
          Testnet Mode Active
===============================================

╭────────────────────────────────────────────────╮
│                ORDER REQUEST                   │
├────────────────────────────────────────────────┤
│ Parameter       Value                          │
├────────────────────────────────────────────────┤
│ Symbol          BTCUSDT                        │
│ Side            BUY                            │
│ Type            MARKET                         │
│ Quantity        0.01                           │
╰────────────────────────────────────────────────╯

==================================================

⠋ Sending order to Binance Futures Testnet...

╭────────────────────────────────────────────────╮
│                ORDER RESPONSE                  │
├────────────────────────────────────────────────┤
│ Field                Value                     │
├────────────────────────────────────────────────┤
│ Order ID             1234567890                │
│ Status               FILLED                    │
│ Executed Qty         0.01                      │
│ Average Price        62450.00                  │
│ Transaction Time     2024-07-01 10:30:25 UTC   │
╰────────────────────────────────────────────────╯

==================================================

OK: Order Placed Successfully (Status: FILLED)

Execution Time: 0.42s
```

---

## Sample Logs

```
2024-07-01 10:20:01 | INFO     | trading_bot | Binance client initialised (testnet, url=...)
2024-07-01 10:20:01 | INFO     | trading_bot | MARKET BUY 0.010000 BTCUSDT
2024-07-01 10:20:02 | WARNING  | trading_bot | Attempt 1/3 failed. Retrying in 1.0s...
2024-07-01 10:20:03 | INFO     | trading_bot | Market order response received: orderId=123456789
2024-07-01 10:20:03 | INFO     | trading_bot | Order completed: symbol=BTCUSDT side=BUY type=MARKET qty=0.01 status=FILLED orderId=123456789
```

Logs are written to `logs/app.log` with automatic rotation at 5 MB, retaining 3 backup files.

---

## Error Handling

| Scenario                   | User Message                                        |
|---------------------------|-----------------------------------------------------|
| Invalid API Key           | `ERROR: Authentication failed. Check your API keys.` |
| Network Timeout           | `ERROR: Network error: [details]`                    |
| Connection Refused        | `ERROR: Could not connect to Binance Testnet.`       |
| Invalid Symbol            | `ERROR: Symbol cannot be empty.`                     |
| Invalid Quantity          | `ERROR: Quantity must be greater than zero.`         |
| Missing Limit Price       | `ERROR: Price is required for LIMIT orders.`         |
| Binance API Error         | `ERROR: Binance API error: [message]`                |
| Validation Error          | `ERROR: [specific validation message]`               |
| API Rate Limit            | Automatically retried up to 3 times with backoff     |
| Keyboard Interrupt (Ctrl+C) | Graceful shutdown with clean message               |

Raw Python tracebacks are **never displayed** to the user. All errors are logged with full context to `logs/app.log`.

---

## Testing

Run the test suite with:

```bash
pip install pytest pytest-mock
pytest -v
```

**Test coverage:**

| Module         | Tests | What's tested                                      |
|----------------|-------|---------------------------------------------------|
| validators     | 16    | Symbol, side, type, quantity, price (valid + edge cases) |
| client         | 6     | Connect, ping, market order, limit order (mocked)  |
| orders         | 2     | OrderService formatting and delegation (mocked)    |
| CLI            | 9     | Argparse parsing for all flags and combinations    |

**Total: 33 tests**

---

## Known Limitations

- **Single symbol per run** — The CLI processes one order at a time. Batch/scheduled trading is not supported.
- **No order cancellation** — Placed orders cannot be cancelled via this tool (use Binance dashboard).
- **No WebSocket streaming** — Real-time price data is provided via polling (5s intervals).
- **Binance Testnet only** — This tool is designed exclusively for the Binance Futures Testnet. Production trading is deliberately unsupported.
- **Quantity precision** — Lot size filters from the exchange are not fetched; orders may be rejected if quantity doesn't match the symbol's step size.

---

## Security

- API keys are loaded from `.env` — **never** hardcoded
- `.env` is included in `.gitignore` — cannot be committed
- API keys are **never logged** or printed to console
- Only the testnet URL (non-sensitive) appears in log output

---

## Retry Logic

API requests that fail due to transient errors (timeouts, connection issues, rate limits) are automatically retried **up to 3 times** with exponential backoff (1s → 2s → 4s) before reporting failure.

---

## Future Improvements

- [x] Unit tests with pytest (33 tests)
- [ ] OCO (One-Cancels-Other) orders
- [ ] Stop-loss and take-profit orders
- [ ] Order history and position tracking
- [ ] WebSocket streaming for real-time prices
- [ ] Configuration file for default trading parameters
- [ ] Docker support
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Support for additional exchanges
- [ ] REST API wrapper for web-based control

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Disclaimer

> ⚠️ **This trading bot is for educational and testing purposes only.** It is designed to work exclusively with the Binance Futures Testnet using simulated funds. The authors are not responsible for any financial losses incurred through misuse of this software.
