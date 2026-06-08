# Binance Futures Testnet Trading Bot

Small Python CLI application for placing Binance USDT-M Futures Testnet orders.

## Features

- Places `MARKET` and `LIMIT` orders on Binance Futures Testnet
- Supports `BUY` and `SELL`
- Bonus order type: `STOP_LIMIT`
- Validates CLI input before submitting orders
- Logs requests, responses, dry runs, and errors to a log file
- Separates CLI, validation, order, and API client code

## Setup

1. Create and activate a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Register for Binance Futures Testnet and create API credentials.

4. Export credentials.

```bash
export BINANCE_API_KEY="your_testnet_api_key"
export BINANCE_API_SECRET="your_testnet_api_secret"
```

The app uses this base URL by default:

```text
https://testnet.binancefuture.com
```

## Run Examples

Run commands from the repository root.

### Dry run market order

```bash
python -m bot --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run
```

### Real market order

```bash
python -m bot --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Dry run limit order

```bash
python -m bot --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 120000 --dry-run
```

### Real limit order

```bash
python -m bot --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 120000
```

### Bonus: stop-limit order

```bash
python -m bot --symbol BTCUSDT --side SELL --type STOP_LIMIT --quantity 0.001 --price 119000 --stop-price 119500
```

## Output

The CLI prints:

- order request summary
- order response details: `orderId`, `status`, `executedQty`, and `avgPrice` where available
- success or failure message

## Logging

Default log file:

```text
logs/trading_bot.log
```

You can override it:

```bash
python -m bot --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run --log-file logs/sample_market_order.log
```

Included sample logs:

- `logs/sample_market_order.log`
- `logs/sample_limit_order.log`
- `logs/check_market.log`
- `logs/check_limit.log`

The `sample_*` logs were generated with `--dry-run`. The `check_*` logs can be used for submission evidence when generated from testnet runs with your own API credentials.

## Project Structure

```text
bot/
  cli.py              Command line interface
  client.py           Binance Futures REST client
  orders.py           Order payload builder and submission helper
  validators.py       Input validation and normalization
logs/                 Sample and check run logs
requirements.txt      Python dependency list
```

## Assumptions

- This project targets Binance USDT-M Futures Testnet only.
- API credentials are read from environment variables, not stored in source code.
- `LIMIT` and `STOP_LIMIT` orders use `GTC`.
- `newOrderRespType=RESULT` is requested so the response contains useful execution details.
- Dry-run mode is for validation and demonstration only; it does not place orders.
