# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-07-01

### Added

- Initial release of the Binance Futures Testnet Trading Bot
- CLI interface with `--symbol`, `--side`, `--type`, `--quantity`, `--price`, `--ping` arguments
- MARKET and LIMIT order support for BUY and SELL
- Secure API key management via `.env` file
- Input validation layer with custom exceptions
- Comprehensive logging with `RotatingFileHandler` (5 MB, 3 backups)
- Retry logic with exponential backoff (3 attempts)
- Rich terminal output with `rich` tables and `halo` spinner
- Execution timer for tracking order latency
- ASCII project banner
- Order confirmation prompt
- `--version`, `--verbose`, `--log-level` CLI flags
- Connection test with `--ping`
- MIT License, CONTRIBUTING guide, and changelog
- Unit test suite with `pytest` (mocked API client)
- Sample log files in `demo/` directory
