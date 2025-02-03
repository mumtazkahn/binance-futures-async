# Examples

This guide provides practical examples for common use cases with the Binance Futures WebSocket library.

## Table of Contents
- [Basic Order Operations](#basic-order-operations)
- [Advanced Order Types](#advanced-order-types)
- [Market Data Streaming](#market-data-streaming)
- [User Data Monitoring](#user-data-monitoring)
- [Combined Operations](#combined-operations)

## Basic Order Operations

### Market and Limit Orders

```python
import asyncio
from binance_futures_async import BinanceClient
from binance_futures_async.exceptions import ConnectionError, RequestError

async def basic_orders():
    client = BinanceClient()
    ws_service = None
    
    try:
        ws_service = await client.websocket_service(
            api_key='your_api_key',
            private_key_path='path/to/your/key'
        )

        # Place a market order
        market_order = await ws_service.place_market_order(
            symbol="BTCUSDT",
            side="BUY",
            quantity="0.001"
        )
        print(f"Market order placed: {market_order}")

        # Place a limit order
        limit_order = await ws_service.place_limit_order(
            symbol="BTCUSDT",
            side="BUY",
            quantity="0.001",
            price="50000",
            timeInForce="GTC"
        )
        print(f"Limit order placed: {limit_order}")

    finally:
        if ws_service:
            await ws_service.close()

if __name__ == "__main__":
    asyncio.run(basic_orders())
```

## Advanced Order Types

### Stop Loss and Take Profit Orders

```python
async def advanced_orders():
    client = BinanceClient()
    ws_service = None
    
    try:
        ws_service = await client.websocket_service(
            api_key='your_api_key',
            private_key_path='path/to/your/key'
        )

        # Place a stop-loss order
        stop_loss = await ws_service.place_stop_market_order(
            symbol="BTCUSDT",
            side="SELL",
            quantity="0.001",
            stopPrice="45000"
        )
        print(f"Stop-loss order placed: {stop_loss}")

        # Place a take-profit order
        take_profit = await ws_service.place_take_profit_market_order(
            symbol="BTCUSDT",
            side="SELL",
            quantity="0.001",
            stopPrice="55000"
        )
        print(f"Take-profit order placed: {take_profit}")

        # Place a trailing stop order
        trailing_stop = await ws_service.place_trailing_stop_market_order(
            symbol="BTCUSDT",
            side="SELL",
            quantity="0.001",
            callbackRate="1.0"  # 1% callback rate
        )
        print(f"Trailing stop order placed: {trailing_stop}")

    finally:
        if ws_service:
            await ws_service.close()
```

## Market Data Streaming

### Multiple Market Data Streams

```python
def handle_market_data(message):
    event_type = message.get('e')
    
    if event_type == 'kline':
        handle_kline(message)
    elif event_type == 'aggTrade':
        handle_aggtrade(message)
    elif event_type == 'markPrice':
        handle_markprice(message)

def handle_kline(message):
    k = message['k']
    print(f"Kline {message['s']} {k['i']}: O:{k['o']} H:{k['h']} L:{k['l']} C:{k['c']}")

def handle_aggtrade(message):
    print(f"Trade {message['s']}: Price: {message['p']}, Quantity: {message['q']}")

def handle_markprice(message):
    print(f"Mark Price {message['s']}: {message['p']}")

async def market_streams():
    client = BinanceClient()
    market_service = None
    
    try:
        market_service = await client.market_service(
            message_handler=handle_market_data
        )

        # Subscribe to multiple data types
        await market_service.subscribe_kline(
            symbols=["BTCUSDT", "ETHUSDT"],
            intervals=["1m", "5m"]
        )
        
        await market_service.subscribe_mark_price(
            symbols=["BTCUSDT", "ETHUSDT"]
        )
        
        await market_service.subscribe_aggregate_trade(
            symbols=["BTCUSDT"]
        )

        # Keep connection alive
        while True:
            await asyncio.sleep(1)

    finally:
        if market_service:
            await market_service.close()
```

## User Data Monitoring

### Account and Position Updates

```python
def handle_user_data(message):
    event_type = message.get('e')
    
    if event_type == 'ACCOUNT_UPDATE':
        handle_account_update(message)
    elif event_type == 'ORDER_TRADE_UPDATE':
        handle_order_update(message)
    elif event_type == 'MARGIN_CALL':
        handle_margin_call(message)

def handle_account_update(message):
    data = message['a']
    print("\nAccount Update:")
    print(f"Reason: {data['m']}")
    
    # Balance updates
    for balance in data.get('B', []):
        print(f"Asset: {balance['a']}, Wallet Balance: {balance['wb']}")
    
    # Position updates
    for position in data.get('P', []):
        print(f"Symbol: {position['s']}, Position: {position['pa']}, Entry Price: {position['ep']}")

def handle_order_update(message):
    data = message['o']
    print("\nOrder Update:")
    print(f"Symbol: {data['s']}")
    print(f"Side: {data['S']}")
    print(f"Type: {data['o']}")
    print(f"Status: {data['X']}")

def handle_margin_call(message):
    print("\nMargin Call!")
    positions = message.get('p', [])
    for position in positions:
        print(f"Symbol: {position['s']}, Position Amount: {position['ps']}")

async def user_data_monitoring():
    client = BinanceClient()
    user_stream = None
    
    try:
        user_stream = await client.user_stream(
            api_key='your_api_key',
            message_handler=handle_user_data
        )

        # Keep connection alive
        while True:
            await asyncio.sleep(1)

    finally:
        if user_stream:
            await user_stream.stop()
```

## Combined Operations

### Trading Bot Example

```python
class TradingBot:
    def __init__(self):
        self.client = BinanceClient()
        self.ws_service = None
        self.market_service = None
        self.user_stream = None
        self.positions = {}
        self.last_price = None

    async def start(self):
        # Initialize all services
        self.ws_service = await self.client.websocket_service(
            api_key='your_api_key',
            private_key_path='path/to/your/key'
        )
        
        self.market_service = await self.client.market_service(
            message_handler=self.handle_market_data
        )
        
        self.user_stream = await self.client.user_stream(
            api_key='your_api_key',
            message_handler=self.handle_user_data
        )

        # Subscribe to market data
        await self.market_service.subscribe_mark_price(
            symbols=["BTCUSDT"]
        )

    def handle_market_data(self, message):
        if message.get('e') == 'markPrice':
            self.last_price = float(message['p'])
            asyncio.create_task(self.check_trading_conditions())

    def handle_user_data(self, message):
        if message.get('e') == 'ACCOUNT_UPDATE':
            for position in message['a'].get('P', []):
                self.positions[position['s']] = float(position['pa'])

    async def check_trading_conditions(self):
        if not self.last_price:
            return

        position = self.positions.get('BTCUSDT', 0)

        try:
            if position == 0 and self.should_open_position():
                await self.open_position()
            elif position != 0 and self.should_close_position():
                await self.close_position()
        except Exception as e:
            print(f"Error in trading logic: {e}")

    def should_open_position(self):
        # Implement your trading logic here
        return False

    def should_close_position(self):
        # Implement your trading logic here
        return False

    async def open_position(self):
        await self.ws_service.place_market_order(
            symbol="BTCUSDT",
            side="BUY",
            quantity="0.001"
        )

    async def close_position(self):
        await self.ws_service.place_market_order(
            symbol="BTCUSDT",
            side="SELL",
            quantity="0.001"
        )

    async def stop(self):
        if self.ws_service:
            await self.ws_service.close()
        if self.market_service:
            await self.market_service.close()
        if self.user_stream:
            await self.user_stream.stop()

async def run_trading_bot():
    bot = TradingBot()
    try:
        await bot.start()
        while True:
            await asyncio.sleep(1)
    finally:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(run_trading_bot())
```

## Next Steps

- Check out the [Configuration Guide](configuration.md) for customization options
- View the [API Reference](../api/client.md) for detailed documentation
- Return to the [Getting Started](getting_started.md) guide