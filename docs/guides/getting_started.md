# Getting Started

This guide will help you get up and running with the Binance Futures WebSocket library.

## Prerequisites

- Python 3.7 or higher
- A Binance Futures account
- API Key and one of the following:
    - Ed25519 key (.pem file)
    - RSA key (.pem file)
    - HMAC secret key

## Installation

```bash
pip install binance-futures-websocket
```

## Basic Usage

The library provides three main components:
1. WebSocket API (for orders and account management)
2. Market Streams (for market data)
3. User Data Streams (for account updates)

### WebSocket API Setup

```python
import asyncio
from binance_futures_async import BinanceClient
from binance_futures_async.exceptions import ConnectionError, AuthenticationError

async def main():
    # Initialize the client
    client = BinanceClient()
    
    # Connect to WebSocket API
    ws_service = await client.websocket_service(
        api_key='your_api_key',
        private_key_path='path/to/your/key'  # .pem file or HMAC secret
    )
    
    # Place a market order
    try:
        response = await ws_service.place_market_order(
            symbol="BTCUSDT",
            side="BUY",
            quantity="0.001"
        )
        print(f"Order placed: {response}")
    finally:
        await ws_service.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Market Streams Setup

```python
from binance_futures_async import BinanceClient

def handle_market_data(message):
    print(f"Received market data: {message}")

async def main():
    client = BinanceClient()
    
    # Initialize market streams
    market_service = await client.market_service(
        message_handler=handle_market_data
    )
    
    # Subscribe to various data streams
    await market_service.subscribe_kline(
        symbols=["BTCUSDT"],
        intervals=["1m"]
    )
    
    # Keep the connection alive
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await market_service.close()
```

### User Data Stream Setup

```python
from binance_futures_async import BinanceClient

def handle_user_data(message):
    print(f"Received user data: {message}")

async def main():
    client = BinanceClient()
    
    # Initialize user data stream
    user_stream = await client.user_stream(
        api_key='your_api_key',
        message_handler=handle_user_data
    )
    
    # Keep the connection alive
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await user_stream.stop()
```

## Message Handlers

Message handlers are crucial for processing stream data. Here's a more detailed example:

```python
def handle_market_data(message):
    # Handle different message types
    event_type = message.get('e')
    
    if event_type == 'kline':
        handle_kline(message)
    elif event_type == 'aggTrade':
        handle_aggtrade(message)
    elif event_type == 'markPrice':
        handle_markprice(message)

def handle_kline(message):
    k = message['k']
    print(f"Symbol: {message['s']}")
    print(f"Interval: {k['i']}")
    print(f"Open: {k['o']}")
    print(f"High: {k['h']}")
    print(f"Low: {k['l']}")
    print(f"Close: {k['c']}")
```

## Error Handling

Always implement proper error handling:

```python
from binance_futures_async.exceptions import (
    ConnectionError,
    AuthenticationError,
    RequestError,
    UserStreamError
)

async def main():
    try:
        # Your code here
        pass
    except ConnectionError as e:
        print(f"Connection error: {e}")
    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
    except RequestError as e:
        print(f"Request failed: {e}")
    except UserStreamError as e:
        print(f"User stream error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

## Next Steps

- Check out the [Configuration](configuration.md) guide for customizing behavior
- See [Examples](examples.md) for more usage scenarios
- Browse the [API Reference](../api/client.md) for detailed documentation