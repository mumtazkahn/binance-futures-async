# WebSocketService

The `WebSocketService` class provides a WebSocket interface for trading operations, account management, and market data retrieval on Binance Futures.

## Constructor

```python
class WebSocketService:
    def __init__(
        self, 
        api_key: str, 
        private_key_path: str, 
        enable_validation: bool = False, 
        config: Dict[str, Any] = None
    ):
```

Creates a new WebSocketService instance with specified authentication and configuration.

**Parameters:**
- `api_key` (str): Your Binance API key
- `private_key_path` (str): Path to private key file (Ed25519/RSA) or HMAC secret
- `enable_validation` (bool, optional): Enable order parameter validation. Defaults to False
- `config` (Dict[str, Any], optional): Custom configuration options

## Connection Methods

### connect

```python
async def connect(self) -> None
```

Establishes the WebSocket connection.

**Raises:**
- `ConnectionError`: If connection cannot be established

### close

```python
async def close(self) -> None
```

Closes the WebSocket connection and cleans up resources.

### login

```python
async def login(self, wait_for_response: bool = True) -> Dict[str, Any]
```

Initiates a session login (Ed25519 keys only).

**Parameters:**
- `wait_for_response` (bool): Whether to wait for server response

**Returns:**
- Response from the server

**Raises:**
- `AuthenticationError`: If login fails or using non-Ed25519 keys

### logout

```python
async def logout(self, wait_for_response: bool = True) -> Dict[str, Any]
```

Terminates the current session.

**Parameters:**
- `wait_for_response` (bool): Whether to wait for server response

**Returns:**
- Response from the server

## Market Data Methods

### get_depth

```python
async def get_depth(
    self, 
    symbol: str, 
    limit: Optional[int] = None, 
    wait_for_response: bool = True
) -> Dict[str, Any]
```

Retrieves order book depth for a symbol.

**Parameters:**
- `symbol` (str): Trading pair symbol (e.g., "BTCUSDT")
- `limit` (int, optional): Number of price levels to retrieve
- `wait_for_response` (bool): Whether to wait for response

**Example:**
```python
depth = await ws_service.get_depth("BTCUSDT", limit=10)
```

### get_ticker_price

```python
async def get_ticker_price(
    self, 
    symbol: Optional[str] = None, 
    wait_for_response: bool = True
) -> Dict[str, Any]
```

Retrieves latest price for a symbol or all symbols.

**Parameters:**
- `symbol` (str, optional): Trading pair symbol. If None, returns all symbols
- `wait_for_response` (bool): Whether to wait for response

**Example:**
```python
# Single symbol
btc_price = await ws_service.get_ticker_price("BTCUSDT")

# All symbols
all_prices = await ws_service.get_ticker_price()
```

### get_ticker_book

```python
async def get_ticker_book(
    self, 
    symbol: Optional[str] = None, 
    wait_for_response: bool = True
) -> Dict[str, Any]
```

Retrieves best bid/ask prices for a symbol or all symbols.

**Parameters:**
- `symbol` (str, optional): Trading pair symbol. If None, returns all symbols
- `wait_for_response` (bool): Whether to wait for response

**Example:**
```python
book_ticker = await ws_service.get_ticker_book("BTCUSDT")
```

## Account Methods

### get_position_info

```python
async def get_position_info(
    self, 
    symbol: str = None, 
    wait_for_response: bool = True
) -> Dict[str, Any]
```

Retrieves current position information.

**Parameters:**
- `symbol` (str, optional): Trading pair symbol. If None, returns all positions
- `wait_for_response` (bool): Whether to wait for response

**Example:**
```python
# Single symbol position
btc_position = await ws_service.get_position_info("BTCUSDT")

# All positions
all_positions = await ws_service.get_position_info()
```

### get_account_balance

```python
async def get_account_balance(
    self, 
    wait_for_response: bool = True
) -> Dict[str, Any]
```

Retrieves current account balance information.

**Example:**
```python
balance = await ws_service.get_account_balance()
```

### get_account_status

```python
async def get_account_status(
    self, 
    wait_for_response: bool = True
) -> Dict[str, Any]
```

Retrieves current account status information.

**Example:**
```python
status = await ws_service.get_account_status()
```

## Order Methods

### place_limit_order

```python
async def place_limit_order(
    self, 
    wait_for_response: bool = True, 
    **kwargs
) -> Dict[str, Any]
```

Places a limit order.

**Required Parameters:**
- `symbol` (str): Trading pair symbol
- `side` (str): "BUY" or "SELL"
- `quantity` (str): Order quantity
- `price` (str): Order price
- `timeInForce` (str): Time in force type

**Optional Parameters:**
- `positionSide` (str): "LONG", "SHORT", or "BOTH"
- `reduceOnly` (bool): Reduce position only
- `newClientOrderId` (str): Custom client order ID
- `stopPrice` (str): Stop price for stop orders
- `workingType` (str): "MARK_PRICE" or "CONTRACT_PRICE"
- `priceProtect` (bool): Price protection flag
- `newOrderRespType` (str): "ACK" or "RESULT"
- `selfTradePreventionMode` (str): Self-trade prevention mode

**Example:**
```python
order = await ws_service.place_limit_order(
    symbol="BTCUSDT",
    side="BUY",
    quantity="0.001",
    price="50000",
    timeInForce="GTC",
    positionSide="LONG",
    reduceOnly=False
)
```

### place_market_order

```python
async def place_market_order(
    self, 
    wait_for_response: bool = True, 
    **kwargs
) -> Dict[str, Any]
```

Places a market order.

**Required Parameters:**
- `symbol` (str): Trading pair symbol
- `side` (str): "BUY" or "SELL"
- `quantity` (str): Order quantity

**Example:**
```python
order = await ws_service.place_market_order(
    symbol="BTCUSDT",
    side="BUY",
    quantity="0.001"
)
```

### place_stop_order

```python
async def place_stop_order(
    self, 
    wait_for_response: bool = True, 
    **kwargs
) -> Dict[str, Any]
```

Places a stop order.

**Required Parameters:**
- `symbol` (str): Trading pair symbol
- `side` (str): "BUY" or "SELL"
- `quantity` (str): Order quantity
- `price` (str): Order price
- `stopPrice` (str): Stop trigger price

**Example:**
```python
order = await ws_service.place_stop_order(
    symbol="BTCUSDT",
    side="SELL",
    quantity="0.001",
    price="45000",
    stopPrice="46000"
)
```

### place_stop_market_order

```python
async def place_stop_market_order(
    self, 
    wait_for_response: bool = True, 
    **kwargs
) -> Dict[str, Any]
```

Places a stop market order.

**Required Parameters:**
- `symbol` (str): Trading pair symbol
- `side` (str): "BUY" or "SELL"
- `stopPrice` (str): Stop trigger price
- Either:
  - `quantity` (str): Order quantity
  - `closePosition` (bool): True to close position

**Example:**
```python
order = await ws_service.place_stop_market_order(
    symbol="BTCUSDT",
    side="SELL",
    stopPrice="46000",
    quantity="0.001"
)
```

### place_take_profit_order

```python
async def place_take_profit_order(
    self, 
    wait_for_response: bool = True, 
    **kwargs
) -> Dict[str, Any]
```

Places a take-profit limit order.

**Required Parameters:**
- `symbol` (str): Trading pair symbol
- `side` (str): "BUY" or "SELL"
- `quantity` (str): Order quantity
- `price` (str): Order price
- `stopPrice` (str): Stop trigger price

**Example:**
```python
order = await ws_service.place_take_profit_order(
    symbol="BTCUSDT",
    side="SELL",
    quantity="0.001",
    price="55000",
    stopPrice="54000"
)
```

### place_take_profit_market_order

```python
async def place_take_profit_market_order(
    self, 
    wait_for_response: bool = True, 
    **kwargs
) -> Dict[str, Any]
```

Places a take-profit market order.

**Required Parameters:**
- `symbol` (str): Trading pair symbol
- `side` (str): "BUY" or "SELL"
- `stopPrice` (str): Stop trigger price
- Either:
  - `quantity` (str): Order quantity
  - `closePosition` (bool): True to close position

**Example:**
```python
order = await ws_service.place_take_profit_market_order(
    symbol="BTCUSDT",
    side="SELL",
    stopPrice="54000",
    quantity="0.001"
)
```

### place_trailing_stop_market_order

```python
async def place_trailing_stop_market_order(
    self, 
    wait_for_response: bool = True, 
    **kwargs
) -> Dict[str, Any]
```

Places a trailing stop market order.

**Required Parameters:**
- `symbol` (str): Trading pair symbol
- `side` (str): "BUY" or "SELL"
- `quantity` (str): Order quantity
- `callbackRate` (str): Callback rate in percent

**Optional Parameters:**
- `activationPrice` (str): Activation price

**Example:**
```python
order = await ws_service.place_trailing_stop_market_order(
    symbol="BTCUSDT",
    side="SELL",
    quantity="0.001",
    callbackRate="1.0",
    activationPrice="50000"
)
```

## Complete Usage Example

```python
import asyncio
from binance_futures_async import BinanceClient
from binance_futures_async.exceptions import (
    ConnectionError,
    AuthenticationError,
    RequestError,
    OrderValidationError
)

async def main():
    client = BinanceClient()
    ws_service = None
    
    try:
        # Initialize service
        ws_service = await client.websocket_service(
            api_key="your_api_key",
            private_key_path="path/to/your/key",
            enable_validation=True
        )
        
        # Connect and login (Ed25519 only)
        await ws_service.login()
        
        # Get account information
        balance = await ws_service.get_account_balance()
        positions = await ws_service.get_position_info()
        
        # Place orders
        limit_order = await ws_service.place_limit_order(
            symbol="BTCUSDT",
            side="BUY",
            quantity="0.001",
            price="50000",
            timeInForce="GTC"
        )
        
        stop_loss = await ws_service.place_stop_market_order(
            symbol="BTCUSDT",
            side="SELL",
            quantity="0.001",
            stopPrice="48000"
        )
        
        take_profit = await ws_service.place_take_profit_market_order(
            symbol="BTCUSDT",
            side="SELL",
            quantity="0.001",
            stopPrice="52000"
        )
        
    except ConnectionError as e:
        print(f"Connection error: {e}")
    except AuthenticationError as e:
        print(f"Authentication error: {e}")
    except RequestError as e:
        print(f"Request error: {e}")
    except OrderValidationError as e:
        print(f"Order validation error: {e}")
    finally:
        if ws_service:
            await ws_service.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Error Handling

The WebSocketService can raise several types of exceptions:

- `ConnectionError`: Connection issues
- `AuthenticationError`: Authentication failures
- `RequestError`: Request failures
- `OrderValidationError`: Order validation failures (if enabled)

## Best Practices

1. **Connection Management**
   - Always use async context managers or try/finally blocks
   - Implement reconnection logic for production systems
   - Handle connection loss gracefully

2. **Order Management**
   - Enable validation for production systems
   - Use appropriate order types for your strategy
   - Implement proper error handling for orders

3. **Performance**
   - Use `wait_for_response=False` for fire-and-forget operations
   - Batch operations when possible
   - Monitor rate limits

4. **Security**
   - Use Ed25519 keys with session login when possible
   - Keep API keys secure
   - Implement proper access controls