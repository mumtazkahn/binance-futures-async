# BinanceClient

The `BinanceClient` class is the main entry point for interacting with Binance Futures WebSocket APIs. It provides access to three core services:

- WebSocket API for orders, account data, and market information
- User Data Streams for real-time account updates
- Market Streams for real-time market data

## Constructor

```python
class BinanceClient:
    def __init__(self):
```

Creates a new BinanceClient instance. The client initializes without any immediate connections - services are created on demand when requested.

## Methods

### websocket_service

```python
async def websocket_service(
    self,
    api_key: str,
    private_key_path: str,
    enable_validation: bool = False,
    config: Dict[str, Any] = None
) -> WebSocketService
```

Initializes and returns a WebSocket service for interacting with Binance Futures WebSocket API.

**Parameters:**
- `api_key` (str): Your Binance API key
- `private_key_path` (str): Path to your private key file or HMAC secret
- `enable_validation` (bool, optional): Enable order validation. Defaults to False
- `config` (Dict[str, Any], optional): Custom configuration options

**Returns:**
- `WebSocketService`: An initialized WebSocket service instance

**Default Configuration:**
```python
DEFAULT_WEBSOCKET_CONFIG = {
    'return_rate_limits': True,      # Return rate limit info
    'connection_timeout': 30,        # Connection timeout (seconds)
    'request_timeout': 30,           # Request timeout (seconds)
    'ping_interval': 180,           # WebSocket ping interval
    'reconnect_delay': 5,           # Initial reconnect delay
    'max_reconnect_delay': 300,     # Maximum reconnect delay
    'max_reconnect_attempts': 5      # Maximum reconnection attempts
}
```

**Example:**
```python
client = BinanceClient()
ws_service = await client.websocket_service(
    api_key="your_api_key",
    private_key_path="path/to/your/key",
    enable_validation=True,
    config={
        'connection_timeout': 60,
        'request_timeout': 15
    }
)
```

### user_stream

```python
async def user_stream(
    self,
    api_key: str,
    message_handler: Callable[[Dict[str, Any]], None],
    config: Dict[str, Any] = None
) -> UserDataStreamAPI
```

Initializes and returns a User Data Stream for receiving real-time account updates.

**Parameters:**
- `api_key` (str): Your Binance API key
- `message_handler` (Callable): Callback function to handle incoming messages
- `config` (Dict[str, Any], optional): Custom configuration options

**Returns:**
- `UserDataStreamAPI`: An initialized user data stream instance

**Default Configuration:**
```python
DEFAULT_USER_STREAM_CONFIG = {
    'connection_timeout': 30,        # Connection timeout (seconds)
    'request_timeout': 30,           # Request timeout (seconds)
    'ping_interval': 3300,          # Listen key keepalive interval (55 minutes)
    'reconnect_delay': 5,           # Initial reconnect delay
    'max_reconnect_delay': 300,     # Maximum reconnect delay
    'max_reconnect_attempts': 5,     # Maximum reconnection attempts
    'health_check_interval': 60      # Health check interval (seconds)
}
```

**Example:**
```python
def handle_user_data(message):
    print(f"Received user data: {message}")

client = BinanceClient()
user_stream = await client.user_stream(
    api_key="your_api_key",
    message_handler=handle_user_data,
    config={
        'health_check_interval': 30
    }
)
```

### market_service

```python
async def market_service(
    self,
    message_handler: Callable[[Dict[str, Any]], None],
    config: Dict[str, Any] = None
) -> MarketService
```

Initializes and returns a Market Service for subscribing to real-time market data streams.

**Parameters:**
- `message_handler` (Callable): Callback function to handle incoming messages
- `config` (Dict[str, Any], optional): Custom configuration options

**Returns:**
- `MarketService`: An initialized market service instance

**Default Configuration:**
```python
DEFAULT_MARKET_STREAM_CONFIG = {
    'connection_timeout': 30,        # Connection timeout (seconds)
    'request_timeout': 30,           # Request timeout (seconds)
    'ping_interval': 180,           # WebSocket ping interval
    'reconnect_delay': 5,           # Initial reconnect delay
    'max_reconnect_delay': 300,     # Maximum reconnect delay
    'max_reconnect_attempts': 5      # Maximum reconnection attempts
}
```

**Example:**
```python
def handle_market_data(message):
    print(f"Received market data: {message}")

client = BinanceClient()
market_service = await client.market_service(
    message_handler=handle_market_data,
    config={
        'ping_interval': 300
    }
)
```

## Error Handling

The client's methods can raise several types of exceptions:

- `ConnectionError`: When connection issues occur
- `AuthenticationError`: When authentication fails
- `RequestError`: When requests fail
- `UserStreamError`: When user stream operations fail
- `OrderValidationError`: When order validation fails (if enabled)

Example with error handling:

```python
from binance_futures_async import BinanceClient
from binance_futures_async.exceptions import (
    ConnectionError,
    AuthenticationError,
    RequestError
)

async def main():
    client = BinanceClient()
    ws_service = None
    
    try:
        ws_service = await client.websocket_service(
            api_key="your_api_key",
            private_key_path="path/to/your/key"
        )
        
        # Use the service...
        
    except ConnectionError as e:
        print(f"Connection error: {e}")
    except AuthenticationError as e:
        print(f"Authentication error: {e}")
    except RequestError as e:
        print(f"Request error: {e}")
    finally:
        if ws_service:
            await ws_service.close()
```

## Best Practices

1. **Service Lifecycle**
   - Create a single client instance for your application
   - Properly close services when they're no longer needed
   - Handle reconnection scenarios using try/except blocks

2. **Configuration**
   - Use default configurations for most cases
   - Adjust timeouts based on network conditions
   - Increase health check frequency for critical applications

3. **Message Handlers**
   - Keep message handlers lightweight
   - Avoid blocking operations in handlers
   - Use proper exception handling in handlers

4. **Error Handling**
   - Always implement proper error handling
   - Use specific exception types for different scenarios
   - Implement reconnection logic for production systems

Example of a well-structured application:

```python
import asyncio
from binance_futures_async import BinanceClient
from binance_futures_async.exceptions import (
    ConnectionError,
    AuthenticationError,
    RequestError,
    UserStreamError
)

async def handle_market_data(message):
    try:
        # Process market data
        print(f"Market update: {message}")
    except Exception as e:
        print(f"Error in market handler: {e}")

async def handle_user_data(message):
    try:
        # Process user data
        print(f"Account update: {message}")
    except Exception as e:
        print(f"Error in user handler: {e}")

async def main():
    client = BinanceClient()
    ws_service = None
    user_stream = None
    market_service = None
    
    try:
        # Initialize services
        ws_service = await client.websocket_service(
            api_key="your_api_key",
            private_key_path="path/to/your/key",
            enable_validation=True
        )
        
        user_stream = await client.user_stream(
            api_key="your_api_key",
            message_handler=handle_user_data
        )
        
        market_service = await client.market_service(
            message_handler=handle_market_data
        )
        
        # Keep application running
        while True:
            await asyncio.sleep(1)
            
    except (ConnectionError, AuthenticationError, RequestError, UserStreamError) as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        if ws_service:
            await ws_service.close()
        if user_stream:
            await user_stream.stop()
        if market_service:
            await market_service.close()

if __name__ == "__main__":
    asyncio.run(main())
```