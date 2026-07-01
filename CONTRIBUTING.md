# Contributing to Trading Bot

Thank you for considering contributing to this project! We welcome contributions that improve code quality, add features, or fix bugs.

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/your-username/trading-bot.git
   ```
3. **Create a virtual environment** and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
4. **Run the tests** to verify everything is working:
   ```bash
   pytest -v
   ```

## Development Guidelines

### Code Style

- Follow **PEP 8** conventions.
- Use **type hints** for all function signatures.
- Write **Google-style docstrings** for all public functions and classes.
- Keep functions focused and small (ideally < 50 lines).

### Testing

- All new features must include **unit tests**.
- Use `pytest` as the test runner.
- Mock external API calls (never hit real Binance endpoints in tests).
- Run the full test suite before submitting a pull request:
  ```bash
  pytest -v --cov=bot
  ```

### Commit Messages

- Use concise, descriptive commit messages.
- Prefix with the area changed, e.g.:
  - `cli: add --log-level flag`
  - `client: fix retry decorator on limit orders`
  - `tests: add validator edge cases`

## Pull Request Process

1. Ensure your branch is up to date with `main`.
2. Run the full test suite and confirm all tests pass.
3. Update the `CHANGELOG.md` with your changes.
4. Open a pull request with a clear title and description.
5. A maintainer will review your PR within a few days.

## Reporting Issues

Open an issue on GitHub with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behaviour
- Python version, OS, and relevant logs

## Code of Conduct

Be respectful, constructive, and inclusive. Harassment or toxic behaviour will not be tolerated.
