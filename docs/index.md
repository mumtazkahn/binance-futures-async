# Binance Futures WebSocket

A high-performance, asynchronous Python library for Binance USD-M Futures latest WebSocket API.

## Features

- Full async implementation
- USD-M Futures latest WebSocket API (including Orders/Position Management)
- USD-M Futures WebSocket Market Streams
- USD-M Futures WebSocket User Streams
- Low latency order placement via WebSocket
- Auto reconnect and health checks
- Auto ping-pong
- Auto keepAlive for listen key for User Streams
- Supports RSA, ED25519 and HMAC keys
- Auto timestamp and request IDs
- Fully configurable for advanced users

## Installation

```bash
pip install binance-futures-async
```

## Quick Example

```python
import asyncio
from binance_futures_async import BinanceClient
from binance_futures_async.exceptions import ConnectionError, AuthenticationError, RequestError

async def main():
    client = BinanceClient()
    ws_service = None
    
    try:
        # Connect to WebSocket API with your credentials
        ws_service = await client.websocket_service(
            api_key='your_api_key',
            private_key_path='path/to/your/key'
        )

        # Get account balance
        balance = await ws_service.get_account_balance()
        print(f'Account balance: {balance}')

    except Exception as e:
        print(f'Error: {e}')
    finally:
        if ws_service:
            await ws_service.close()

if __name__ == '__main__':
    asyncio.run(main())
```

## Components

The library consists of three main components:

### 1. WebSocket API
Low-latency interface for orders, account data, and market information.

### 2. Market Streams
Real-time market data streams including:
- Aggregate trades
- Mark price updates
- Kline/candlestick data
- Order book updates
- Liquidation orders

### 3. User Data Streams
Real-time account updates including:
- Account balance changes
- Order updates
- Position updates
- Margin calls

## Next Steps

- Check out the [Getting Started](guides/getting_started.md) guide
- See [Configuration](guides/configuration.md) options
- View [Examples](guides/examples.md)
- Browse the [API Reference](api/client.md)