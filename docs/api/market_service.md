# MarketService

The `MarketService` class provides real-time market data streaming capabilities for Binance Futures, including aggregated trades, klines (candlesticks), mark prices, liquidations, and order book updates.

## Constructor

```python
class MarketService:
    def __init__(
        self,
        base_url: str,
        message_handler: Callable[[Dict[str, Any]], None],
        config: Dict[str, Any]
    ):
```

Creates a new MarketService instance.

**Parameters:**
- `base_url` (str): WebSocket base URL ("wss://fstream.binance.com")
- `message_handler` (Callable): Function to handle incoming market data messages
- `config` (Dict[str, Any]): Configuration options

**Supported Intervals:**
```python
valid_intervals = [
    '1m', '3m', '5m', '15m', '30m',
    '1h', '2h', '4h', '6h', '8h', '12h',
    '1d', '3d', '1w', '1M'
]
```

**Contract Types:**
```python
valid_contract_types = ['perpetual', 'current_quarter', 'next_quarter']
```

## Connection Methods

### connect

```python
async def connect(self) -> None
```

Establishes the WebSocket connection.

### close

```python
async def close(self) -> None
```

Closes the WebSocket connection and cleans up resources.

## Market Data Stream Methods

### Aggregate Trade Streams

```python
async def subscribe_aggregate_trade(
    self, 
    symbols: List[str]
) -> Dict[str, Any]
```

Subscribe to aggregate trade updates for specified symbols.

**Parameters:**
- `symbols` (List[str]): List of trading pair symbols

**Example:**
```python
await market_service.subscribe_aggregate_trade(["BTCUSDT", "ETHUSDT"])
```

```python
async def unsubscribe_aggregate_trade(
    self, 
    symbols: List[str]
) -> Dict[str, Any]
```

Unsubscribe from aggregate trade updates.

### Mark Price Streams

```python
async def subscribe_mark_price(
    self, 
    symbols: List[str], 
    update_speed: str = "3000ms"
) -> Dict[str, Any]
```

Subscribe to mark price updates for specified symbols.

**Parameters:**
- `symbols` (List[str]): List of trading pair symbols
- `update_speed` (str): Update frequency, either "3000ms" or "1000ms"

**Example:**
```python
await market_service.subscribe_mark_price(
    symbols=["BTCUSDT", "ETHUSDT"],
    update_speed="1000ms"
)
```

```python
async def subscribe_all_mark_price(
    self, 
    update_speed: str = "3000ms"
) -> Dict[str, Any]
```

Subscribe to mark price updates for all symbols.

### Kline/Candlestick Streams

```python
async def subscribe_kline(
    self, 
    symbols: List[str], 
    intervals: List[str]
) -> Dict[str, Any]
```

Subscribe to kline/candlestick updates for specified symbols and intervals.

**Parameters:**
- `symbols` (List[str]): List of trading pair symbols
- `intervals` (List[str]): List of kline intervals

**Example:**
```python
await market_service.subscribe_kline(
    symbols=["BTCUSDT"],
    intervals=["1m", "5m", "1h"]
)
```

### Continuous Contract Kline Streams

```python
async def subscribe_continuous_kline(
    self, 
    pairs: List[str], 
    contract_types: List[str], 
    intervals: List[str]
) -> Dict[str, Any]
```

Subscribe to continuous contract kline updates.

**Parameters:**
- `pairs` (List[str]): List of trading pairs
- `contract_types` (List[str]): List of contract types
- `intervals` (List[str]): List of kline intervals

**Example:**
```python
await market_service.subscribe_continuous_kline(
    pairs=["BTCUSDT"],
    contract_types=["perpetual"],
    intervals=["1m", "5m"]
)
```

### Mini Ticker Streams

```python
async def subscribe_mini_ticker(
    self, 
    symbols: List[str]
) -> Dict[str, Any]
```

Subscribe to mini ticker updates for specified symbols.

```python
async def subscribe_all_market_mini_tickers(self) -> Dict[str, Any]
```

Subscribe to mini ticker updates for all market symbols.

### Market Ticker Streams

```python
async def subscribe_symbol_ticker(
    self, 
    symbols: List[str]
) -> Dict[str, Any]
```

Subscribe to individual symbol ticker updates.

```python
async def subscribe_all_market_tickers(self) -> Dict[str, Any]
```

Subscribe to ticker updates for all market symbols.

### Book Ticker Streams

```python
async def subscribe_book_ticker(
    self, 
    symbols: List[str]
) -> Dict[str, Any]
```

Subscribe to best bid/ask updates for specified symbols.

```python
async def subscribe_all_book_tickers(self) -> Dict[str, Any]
```

Subscribe to book ticker updates for all symbols.

### Liquidation Order Streams

```python
async def subscribe_liquidation_order(
    self, 
    symbols: List[str]
) -> Dict[str, Any]
```

Subscribe to liquidation order events for specified symbols.

```python
async def subscribe_all_liquidation_orders(self) -> Dict[str, Any]
```

Subscribe to all liquidation order events.

### Partial Book Depth Streams

```python
async def subscribe_partial_book_depth(
    self, 
    symbols: List[str], 
    levels: int, 
    update_speed: int = 250
) -> Dict[str, Any]
```

Subscribe to partial order book updates.

**Parameters:**
- `symbols` (List[str]): List of trading pair symbols
- `levels` (int): Depth levels (5, 10, or 20)
- `update_speed` (int): Update speed in milliseconds (250, 500, or 100)

**Example:**
```python
await market_service.subscribe_partial_book_depth(
    symbols=["BTCUSDT"],
    levels=10,
    update_speed=100
)
```

### Diff. Book Depth Streams

```python
async def subscribe_diff_book_depth(
    self, 
    symbols: List[str], 
    update_speed: int = 250
) -> Dict[str, Any]
```

Subscribe to order book difference updates.

### Composite Index Streams

```python
async def subscribe_composite_index(
    self, 
    symbols: List[str]
) -> Dict[str, Any]
```

Subscribe to composite index information.

### Asset Index Streams

```python
async def subscribe_asset_index(
    self, 
    asset_symbols: List[str]
) -> Dict[str, Any]
```

Subscribe to multi-assets mode asset index updates.

## Complete Usage Example

```python
import asyncio
from binance_futures_async import BinanceClient
from binance_futures_async.exceptions import ConnectionError, RequestError

async def handle_market_data(message: Dict[str, Any]):
    """Process incoming market data messages."""
    if message.get('e') == 'kline':
        # Handle kline/candlestick update
        kline = message['k']
        print(f"Kline update for {message['s']}:")
        print(f"Interval: {kline['i']}")
        print(f"Close: {kline['c']}")
    elif message.get('e') == 'aggTrade':
        # Handle aggregate trade
        print(f"Trade: {message['s']} Price: {message['p']}")
    elif message.get('e') == 'markPrice':
        # Handle mark price update
        print(f"Mark price: {message['s']} Price: {message['p']}")

async def main():
    client = BinanceClient()
    market_service = None
    
    try:
        # Initialize market service
        market_service = await client.market_service(
            message_handler=handle_market_data
        )
        
        # Subscribe to multiple data streams
        await market_service.subscribe_kline(
            symbols=["BTCUSDT"],
            intervals=["1m", "5m"]
        )
        
        await market_service.subscribe_mark_price(
            symbols=["BTCUSDT"],
            update_speed="1000ms"
        )
        
        await market_service.subscribe_aggregate_trade(
            symbols=["BTCUSDT"]
        )
        
        # Keep the connection alive
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

## Message Handling

Example of a comprehensive message handler:

```python
async def handle_market_data(message: Dict[str, Any]):
    """Handle different types of market data messages."""
    try:
        event_type = message.get('e')
        
        if event_type == 'kline':
            handle_kline_update(message)
        elif event_type == 'aggTrade':
            handle_aggregate_trade(message)
        elif event_type == 'markPrice':
            handle_mark_price_update(message)
        elif event_type == 'bookTicker':
            handle_book_ticker(message)
        elif event_type == 'forceOrder':
            handle_liquidation_order(message)
        elif event_type == 'depth':
            handle_depth_update(message)
            
    except Exception as e:
        print(f"Error processing message: {e}")

def handle_kline_update(message):
    kline = message['k']
    print(f"""
    Symbol: {message['s']}
    Interval: {kline['i']}
    Open: {kline['o']}
    High: {kline['h']}
    Low: {kline['l']}
    Close: {kline['c']}
    Volume: {kline['v']}
    """)

def handle_aggregate_trade(message):
    print(f"""
    Symbol: {message['s']}
    Price: {message['p']}
    Quantity: {message['q']}
    """)

def handle_mark_price_update(message):
    print(f"""
    Symbol: {message['s']}
    Mark Price: {message['p']}
    Estimated Settlement Price: {message['P']}
    """)
```

## Best Practices

1. **Connection Management**
   - Implement proper reconnection logic
   - Use try/finally blocks for cleanup
   - Monitor connection health

2. **Subscription Management**
   - Group related subscriptions
   - Maintain list of active subscriptions
   - Implement proper unsubscribe logic

3. **Message Handling**
   - Keep handlers lightweight
   - Process messages asynchronously
   - Implement proper error handling

4. **Performance Optimization**
   - Use appropriate update speeds
   - Subscribe only to needed data
   - Implement message queuing if needed

5. **Resource Management**
   - Clean up resources properly
   - Monitor memory usage
   - Implement circuit breakers

## Error Handling

The MarketService can raise these exceptions:

- `ConnectionError`: Connection issues
- `RequestError`: Subscription/unsubscription failures

Example error handling:

```python
try:
    await market_service.subscribe_kline(
        symbols=["BTCUSDT"],
        intervals=["1m"]
    )
except ConnectionError as e:
    print(f"Connection error: {e}")
    # Implement reconnection logic
except RequestError as e:
    print(f"Subscription error: {e}")
    # Handle subscription failure
```