# Binance Futures WebSocket Library

A high-performance, asynchronous Python library for Binance USD-M Futures latest WebSocket API.

### Supports:
- USD-M Futures latest WebSocket API (including Orders/Position Management)
- USD-M Futures WebSocket Market Streams
- USD-M Futures WebSocket User Streams

### Features:
- Full async implementation
- Low latency order placement via WebSocket
- Auto reconnect and health checks
- Auto ping-pong
- Auto keepAlive for listen key for User Streams
- Supports RSA, ED25519 and HMAC keys
- Supports login and skipping of keys and signature for safety and performance
- Auto timestamp and request IDs
- Fully configurable for advanced users

### Installation
```bash
pip install binance-futures-async
```


For detailed setup instructions and best practices, see our [Getting Started Guide](docs/guides/getting_started.md).

# Quick Start

Here's how to get started with the three main components of the library. Each example shows minimal setup with default configurations.

### 1. WebSocket API - Place Orders, Check Account & Market Data

The WebSocket API provides unified, low-latency access to:
- Market Data (depth, ticker price, ticker book)
- Account Information (positions, balance, status) 
- Order Management (limit, market, stop orders and more)

#### Example 1: Place a Limit Order

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
            api_key="your_api_key",
            private_key_path="path/to/your/key"  # Can be:
                                                # - ED25519: path to .pem file
                                                # - RSA: path to .pem file
                                                # - HMAC: your secret key as string
        )

        # Place a limit order for BTC
        response = await ws_service.place_limit_order(
            symbol="BTCUSDT",
            side="BUY",
            quantity="0.001",
            price="50000",
            timeInForce="GTC"
        )
        print(f"Order placed: {response}")

    except ConnectionError as e:
        print(f"Connection error: {e}")
    except AuthenticationError as e:
        print(f"Authentication error: {e}")
    except RequestError as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if ws_service:
            await ws_service.close()

if __name__ == "__main__":
    asyncio.run(main())
```

#### Example 2: Check Account Balance
```python
async def main():
    client = BinanceClient()
    ws_service = None
    
    try:
        ws_service = await client.websocket_service(
            api_key="your_api_key",
            private_key_path="path/to/your/key"
        )

        # Get account balance
        balance = await ws_service.get_account_balance()
        print(f"Account balance: {balance}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if ws_service:
            await ws_service.close()

if __name__ == "__main__":
    asyncio.run(main())
```

For more examples and detailed API usage, see our [WebSocket Service API documentation](docs/api/websocket_service.md).

### 2. User Data Stream - Monitor Account Updates

```python
import asyncio
from binance_futures_async import BinanceClient
from binance_futures_async.exceptions import ConnectionError, AuthenticationError, UserStreamError

def handle_user_data(message):
    print(f"Received user data: {message}")

async def main():
    client = BinanceClient()
    user_stream = None
    
    try:
        # Initialize user data stream
        user_stream = await client.user_stream(
            api_key="your_api_key",
            message_handler=handle_user_data
        )

        # Keep connection alive
        while True:
            await asyncio.sleep(1)

    except ConnectionError as e:
        print(f"Connection error: {e}")
    except AuthenticationError as e:
        print(f"Authentication error: {e}")
    except UserStreamError as e:
        print(f"User stream error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if user_stream:
            await user_stream.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

For complete details on user data handling, see our [User Data Stream API documentation](docs/api/user_data_stream.md).

### 3. Market Streams - Subscribe to Market Data

```python
import asyncio
from binance_futures_async import BinanceClient
from binance_futures_async.exceptions import ConnectionError, RequestError

def handle_market_data(message):
    print(f"Received market data: {message}")

async def main():
    client = BinanceClient()
    market_service = None
    
    try:
        # Initialize market streams
        market_service = await client.market_service(
            message_handler=handle_market_data
        )

        # Subscribe to BTCUSDT 1m klines
        await market_service.subscribe_kline(
            symbols=["BTCUSDT"],
            intervals=["1m"]
        )
        
        # Keep connection alive
        while True:
            await asyncio.sleep(1)

    except ConnectionError as e:
        print(f"Connection error: {e}")
    except RequestError as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if market_service:
            await market_service.close()

if __name__ == "__main__":
    asyncio.run(main())
```

For all available market data streams and options, see our [Market Service API documentation](docs/api/market_service.md).

# Configuration and Options

The library provides several configuration options for fine-tuning behavior and performance. Each service (WebSocket API, User Data Stream, Market Stream) can be configured independently.

## Default Configurations

Each service comes with sensible defaults:

```python
# WebSocket API defaults
WEBSOCKET_DEFAULTS = {
    'return_rate_limits': True,      # Return rate limit info in responses
    'connection_timeout': 30,        # Connection timeout in seconds
    'request_timeout': 30,           # Individual request timeout
    'ping_interval': 180,           # WebSocket ping interval
    'reconnect_delay': 5,           # Initial reconnection delay
    'max_reconnect_delay': 300,     # Maximum reconnection delay
    'max_reconnect_attempts': 5      # Maximum reconnection attempts
}

# User Data Stream defaults
USER_STREAM_DEFAULTS = {
    'connection_timeout': 30,
    'request_timeout': 30,
    'ping_interval': 3300,          # 55 minutes (listen key keepalive)
    'reconnect_delay': 5,
    'max_reconnect_delay': 300,
    'max_reconnect_attempts': 5,
    'health_check_interval': 60     # Stream health check interval
}

# Market Stream defaults
MARKET_STREAM_DEFAULTS = {
    'connection_timeout': 30,
    'request_timeout': 30,
    'ping_interval': 180,
    'reconnect_delay': 5,
    'max_reconnect_delay': 300,
    'max_reconnect_attempts': 5
}
```

## Using Custom Configurations

You can override any default configuration when initializing services:

```python
from binance_futures_async import BinanceClient

async def main():
    client = BinanceClient()
    
    # WebSocket API with custom config
    ws_service = await client.websocket_service(
        api_key="your_api_key",
        private_key_path="path/to/your/key",
        config={
            'return_rate_limits': False,     # Disable rate limit info
            'connection_timeout': 60,        # Longer timeout
            'request_timeout': 15            # Shorter request timeout
        }
    )

    # Market Streams with custom config
    market_service = await client.market_service(
        message_handler=handle_market_data,
        config={
            'ping_interval': 300,            # Longer ping interval
            'max_reconnect_attempts': 10     # More reconnection attempts
        }
    )
```

## Additional Options

### Order Validation
Enable order validation to catch common errors before sending to Binance:

```python
ws_service = await client.websocket_service(
    api_key="your_api_key",
    private_key_path="path/to/your/key",
    enable_validation=True          # Enable order validation
)
```

### Key Configuration Options Explained

| Parameter | Description | Use Case |
|-----------|-------------|----------|
| `return_rate_limits` | Include rate limit info in responses | Monitor API usage and prevent limits |
| `connection_timeout` | Maximum time to establish connection | Adjust for slower networks |
| `request_timeout` | Maximum time to wait for response | Balance between reliability and latency |
| `ping_interval` | Interval between ping messages | Keep connection alive |
| `reconnect_delay` | Initial wait time before reconnecting | Control reconnection behavior |
| `max_reconnect_delay` | Maximum wait time between attempts | Prevent aggressive reconnections |
| `max_reconnect_attempts` | Maximum number of reconnection tries | Control recovery behavior |
| `health_check_interval` | Interval for checking stream health | Ensure reliable user data streams |
| `enable_validation` | Enable order parameter validation | Catch errors before sending to exchange |


For comprehensive configuration options and advanced usage, see our [Configuration Guide](docs/guides/configuration.md).

### Best Practices

1. **Network Conditions**: Adjust timeouts based on your network reliability:
   ```python
   config = {
       'connection_timeout': 60,    # Longer for unreliable networks
       'request_timeout': 45
   }
   ```

2. **High-Frequency Trading**: Optimize for low latency:
   ```python
   config = {
       'return_rate_limits': False,  # Reduce response payload
       'request_timeout': 10         # Faster timeout for HFT
   }
   ```

3. **Production Systems**: Configure for reliability:
   ```python
   config = {
       'max_reconnect_attempts': 15,  # More reconnection attempts
       'health_check_interval': 30    # More frequent health checks
   }
   ```

# Session Login (Ed25519 Keys Only)

When using Ed25519 keys, the library supports a modern session login feature that enhances both security and performance:

```python
ws_service = await client.websocket_service(
    api_key="your_api_key",
    private_key_path="path/to/ed25519.pem"
)

# Login to start session (Ed25519 only)
await ws_service.login()

# After successful login:
# - No need to transmit API key with each request
# - No need to calculate signatures
# - Improved security and reduced latency
```

Note: 
- The library fully supports RSA and HMAC keys for all operations
- Login feature is only available with Ed25519 keys
- Without login, the library automatically handles key and signature requirements
# Error Handling

The library provides specific exceptions for different types of errors. All exceptions inherit from the base `BinanceWebSocketError` class.

## Exception Types

### `BinanceWebSocketError`
Base exception class for all library-specific errors.

```python
try:
    await ws_service.place_limit_order(...)
except BinanceWebSocketError as e:
    print(f"Library error occurred: {e}")
```

### `ConnectionError`
Raised when there are issues with WebSocket connections.

- Network connectivity issues
- Connection timeouts
- Maximum reconnection attempts reached

```python
try:
    await client.market_service(message_handler=handler)
except ConnectionError as e:
    print(f"Connection failed: {e}")
```

### `AuthenticationError`
Indicates authentication-related failures.

- Invalid API keys
- Invalid signatures
- Session login failures (Ed25519)

```python
try:
    await ws_service.login()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
```

### `RequestError`
Indicates issues with specific WebSocket requests.

- Request timeout
- Invalid parameters
- Rate limit exceeded
- Server response errors

```python
try:
    await ws_service.get_account_balance()
except RequestError as e:
    print(f"Request failed: {e}")
```

### `UserStreamError`
Specific to User Data Stream operations.

- Listen key issues
- Stream initialization failures

```python
try:
    await client.user_stream(api_key, message_handler)
except UserStreamError as e:
    print(f"User stream error: {e}")
```

### `OrderValidationError`
Raised during order parameter validation (when validation is enabled).

- Invalid order parameters
- Missing required fields
- Value range violations

```python
try:
    await ws_service.place_limit_order(
        symbol="BTCUSDT",
        side="INVALID",  # Invalid value
        quantity="0.001",
        price="50000",
        timeInForce="GTC"
    )
except OrderValidationError as e:
    print(f"Order validation failed: {e}")
```

## Documentation
For complete library documentation:
- [Getting Started Guide](docs/guides/getting_started.md)
- [API Reference](docs/api/)
  - [Client API](docs/api/client.md)
  - [WebSocket Service API](docs/api/websocket_service.md)
  - [Market Service API](docs/api/market_service.md)
  - [User Data Stream API](docs/api/user_data_stream.md)
- [Configuration Guide](docs/guides/configuration.md)
- [Examples](docs/guides/examples.md)

