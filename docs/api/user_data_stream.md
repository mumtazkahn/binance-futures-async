# User Data Stream

The User Data Stream provides real-time updates about your Binance Futures account, including:
- Account updates (balances, positions)
- Order updates (execution reports)
- Position updates
- Margin calls

## UserDataStreamAPI

The `UserDataStreamAPI` class provides the main interface for connecting to and managing user data streams.

### Constructor

```python
class UserDataStreamAPI:
    def __init__(
        self,
        api_key: str,
        message_handler: Callable[[Dict[str, Any]], None],
        config: Dict[str, Any]
    ):
```

Creates a new UserDataStreamAPI instance.

**Parameters:**
- `api_key` (str): Your Binance API key
- `message_handler` (Callable): Function to handle incoming user data messages
- `config` (Dict[str, Any]): Configuration options

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

## Methods

### start

```python
async def start(self) -> None
```

Starts the user data stream connection.

**Raises:**
- `ConnectionError`: If connection cannot be established
- `AuthenticationError`: If authentication fails
- `UserStreamError`: If stream initialization fails

### stop

```python
async def stop(self) -> None
```

Stops the user data stream and cleans up resources.

### Properties

```python
@property
def is_connected(self) -> bool
```

Returns the current connection status.

```python
@property
def listen_key(self) -> Optional[str]
```

Returns the current listen key if connected.

## Message Types and Handling

### 1. Account Update Event

Received when your account balance or position changes.

```python
def handle_account_update(message: Dict[str, Any]):
    """Handle account update events."""
    if message['e'] == 'ACCOUNT_UPDATE':
        # Balance updates
        for balance in message['a']['B']:
            print(f"""
            Asset: {balance['a']}
            Wallet Balance: {balance['wb']}
            Cross Wallet Balance: {balance['cw']}
            """)
            
        # Position updates
        for position in message['a']['P']:
            print(f"""
            Symbol: {position['s']}
            Position Amount: {position['pa']}
            Entry Price: {position['ep']}
            Unrealized PNL: {position['up']}
            """)
```

### 2. Order Update Event

Received when an order status changes.

```python
def handle_order_update(message: Dict[str, Any]):
    """Handle order update events."""
    if message['e'] == 'ORDER_TRADE_UPDATE':
        order = message['o']
        print(f"""
        Symbol: {order['s']}
        Client Order ID: {order['c']}
        Side: {order['S']}
        Order Type: {order['o']}
        Price: {order['p']}
        Original Quantity: {order['q']}
        Order Status: {order['X']}
        Last Filled Quantity: {order['l']}
        Last Filled Price: {order['L']}
        """)
```

### 3. Position Update Event

Received when your position risk changes.

```python
def handle_position_update(message: Dict[str, Any]):
    """Handle position update events."""
    if message['e'] == 'ACCOUNT_CONFIG_UPDATE':
        print(f"""
        Symbol: {message['ac']['s']}
        Leverage: {message['ac']['l']}
        """)
```

### 4. Margin Call Event

Received when your position risk level changes significantly.

```python
def handle_margin_call(message: Dict[str, Any]):
    """Handle margin call events."""
    if message['e'] == 'MARGIN_CALL':
        for position in message['p']:
            print(f"""
            Symbol: {position['s']}
            Position Side: {position['ps']}
            Position Amount: {position['pa']}
            Margin Type: {position['mt']}
            Auto-Deleveraging Indicator: {position['iw']}
            """)
```

## Complete Usage Example

```python
import asyncio
from typing import Dict, Any
from binance_futures_async import BinanceClient
from binance_futures_async.exceptions import (
    ConnectionError,
    AuthenticationError,
    UserStreamError
)

class UserDataHandler:
    def __init__(self):
        self.positions = {}
        self.balances = {}
        self.orders = {}

    async def handle_message(self, message: Dict[str, Any]):
        """Handle incoming user data stream messages."""
        try:
            event_type = message.get('e')
            
            if event_type == 'ACCOUNT_UPDATE':
                await self.handle_account_update(message)
            elif event_type == 'ORDER_TRADE_UPDATE':
                await self.handle_order_update(message)
            elif event_type == 'MARGIN_CALL':
                await self.handle_margin_call(message)
            elif event_type == 'ACCOUNT_CONFIG_UPDATE':
                await self.handle_position_update(message)
                
        except Exception as e:
            print(f"Error processing message: {e}")

    async def handle_account_update(self, message: Dict[str, Any]):
        """Process account updates."""
        update = message['a']
        
        # Update balances
        for balance in update['B']:
            asset = balance['a']
            self.balances[asset] = {
                'wallet_balance': balance['wb'],
                'cross_wallet_balance': balance['cw']
            }
        
        # Update positions
        for position in update['P']:
            symbol = position['s']
            self.positions[symbol] = {
                'amount': position['pa'],
                'entry_price': position['ep'],
                'unrealized_pnl': position['up']
            }

    async def handle_order_update(self, message: Dict[str, Any]):
        """Process order updates."""
        order = message['o']
        order_id = order['c']
        
        self.orders[order_id] = {
            'symbol': order['s'],
            'side': order['S'],
            'type': order['o'],
            'status': order['X'],
            'price': order['p'],
            'quantity': order['q']
        }

async def main():
    client = BinanceClient()
    user_stream = None
    handler = UserDataHandler()
    
    try:
        # Initialize user data stream
        user_stream = await client.user_stream(
            api_key="your_api_key",
            message_handler=handler.handle_message,
            config={
                'health_check_interval': 30,  # More frequent health checks
                'ping_interval': 1800         # 30-minute keepalive
            }
        )
        
        print("User data stream started")
        
        # Keep the connection alive
        while True:
            await asyncio.sleep(1)
            
            # Example: Print current positions
            if handler.positions:
                print("\nCurrent Positions:")
                for symbol, pos in handler.positions.items():
                    print(f"{symbol}: {pos['amount']} @ {pos['entry_price']}")
            
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

## Best Practices

1. **Message Handler Design**
   - Keep handlers lightweight
   - Process messages asynchronously when possible
   - Implement proper error handling
   - Use structured logging
   ```python
   async def handle_message(message: Dict[str, Any]):
       try:
           await process_message(message)
       except Exception as e:
           logging.error(f"Error processing message: {e}", exc_info=True)
   ```

2. **State Management**
   - Maintain clean state objects
   - Use thread-safe data structures
   - Implement state recovery mechanisms
   ```python
   from threading import Lock
   
   class AccountState:
       def __init__(self):
           self._lock = Lock()
           self._positions = {}
           
       def update_position(self, symbol: str, data: Dict[str, Any]):
           with self._lock:
               self._positions[symbol] = data
   ```

3. **Connection Management**
   - Implement reconnection logic
   - Monitor connection health
   - Handle listen key expiration
   ```python
   async def maintain_connection(user_stream):
       while True:
           try:
               if not user_stream.is_connected:
                   await user_stream.start()
               await asyncio.sleep(30)
           except Exception as e:
               logging.error(f"Connection error: {e}")
               await asyncio.sleep(5)
   ```

4. **Resource Management**
   - Properly clean up resources
   - Implement graceful shutdown
   - Monitor memory usage
   ```python
   async def shutdown(user_stream):
       try:
           await user_stream.stop()
       except Exception as e:
           logging.error(f"Error during shutdown: {e}")
   ```

5. **Error Handling**
   - Implement comprehensive error handling
   - Use appropriate error types
   - Log errors with context
   ```python
   try:
       await user_stream.start()
   except ConnectionError as e:
       logging.error(f"Connection failed: {e}")
       # Implement retry logic
   except AuthenticationError as e:
       logging.error(f"Authentication failed: {e}")
       # Handle authentication issues
   except UserStreamError as e:
       logging.error(f"Stream error: {e}")
       # Handle stream-specific issues
   ```

## Common Issues and Solutions

1. **Connection Drops**
   ```python
   async def handle_connection_drop():
       retry_count = 0
       while retry_count < MAX_RETRIES:
           try:
               await user_stream.start()
               break
           except ConnectionError:
               retry_count += 1
               await asyncio.sleep(exponential_backoff(retry_count))
   ```

2. **Message Processing Delays**
   ```python
   from asyncio import Queue

   class MessageProcessor:
       def __init__(self):
           self.queue = Queue()
           
       async def process_messages(self):
           while True:
               message = await self.queue.get()
               await self.process_single_message(message)
               self.queue.task_done()
   ```

3. **State Synchronization**
   ```python
   class StateManager:
       async def sync_state(self):
           try:
               # Get current state from REST API
               rest_state = await get_account_state()
               # Update local state
               self.update_local_state(rest_state)
           except Exception as e:
               logging.error(f"State sync failed: {e}")
   ```

## Performance Optimization

1. **Message Filtering**
   ```python
   def filter_messages(message: Dict[str, Any]) -> bool:
       """Filter out unnecessary messages."""
       if message['e'] == 'ACCOUNT_UPDATE':
           return True
       if message['e'] == 'ORDER_TRADE_UPDATE' and \
          message['o']['X'] in ['NEW', 'FILLED', 'CANCELED']:
           return True
       return False
   ```

2. **Batch Processing**
   ```python
   class BatchProcessor:
       def __init__(self, batch_size: int = 100):
           self.batch_size = batch_size
           self.batch = []
           
       async def process_batch(self):
           if len(self.batch) >= self.batch_size:
               await self.flush_batch()
               
       async def flush_batch(self):
           # Process accumulated messages
           pass
   ```

3. **Memory Management**
   ```python
   class MemoryOptimizedHandler:
       def __init__(self, max_cache_size: int = 1000):
           self.cache = collections.OrderedDict()
           self.max_cache_size = max_cache_size
           
       def add_to_cache(self, key: str, value: Any):
           if len(self.cache) >= self.max_cache_size:
               self.cache.popitem(last=False)
           self.cache[key] = value
   ```