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