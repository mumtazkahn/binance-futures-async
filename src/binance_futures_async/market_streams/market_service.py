from typing import (
    Any,
    Callable,
    Dict,
    List,
)

from .market_streams import MarketStreams


class MarketService:
    def __init__(
        self,
        base_url: str,
        message_handler: Callable[[Dict[str, Any]], None],
        config: Dict[str, Any],
    ):

        self.market_streams = MarketStreams(
            base_url=base_url, message_handler=message_handler, config=config
        )

        self.valid_intervals = [
            "1m",
            "3m",
            "5m",
            "15m",
            "30m",
            "1h",
            "2h",
            "4h",
            "6h",
            "8h",
            "12h",
            "1d",
            "3d",
            "1w",
            "1M",
        ]
        self.valid_contract_types = [
            "perpetual",
            "current_quarter",
            "next_quarter",
        ]
        self.valid_depth_levels = [5, 10, 20]
        self.valid_update_speeds = [250, 500, 100]

    async def connect(self):
        await self.market_streams.connect()

    async def close(self):
        await self.market_streams.close()

    async def subscribe_aggregate_trade(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Subscribe to Aggregate Trade Streams for the given symbols.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_aggregate_trade(["BTCUSDT", "ETHUSDT"])
        """
        streams = [f"{symbol.lower()}@aggTrade" for symbol in symbols]
        return await self.market_streams.subscribe(streams)

    async def unsubscribe_aggregate_trade(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Unsubscribe from Aggregate Trade Streams for the given symbols.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_aggregate_trade(["BTCUSDT", "ETHUSDT"])
        """
        streams = [f"{symbol.lower()}@aggTrade" for symbol in symbols]
        return await self.market_streams.unsubscribe(streams)

    async def subscribe_mark_price(
        self, symbols: List[str], update_speed: str = "3000ms"
    ) -> Dict[str, Any]:
        """
        Subscribe to Mark Price Streams for the given symbols.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).
            update_speed (str): The update speed, either "3000ms" (default) or "1000ms".

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_mark_price(["BTCUSDT", "ETHUSDT"], update_speed="1000ms")
        """
        if update_speed not in ["3000ms", "1000ms"]:
            raise ValueError("update_speed must be either '3000ms' or '1000ms'")

        suffix = "@1s" if update_speed == "1000ms" else ""
        streams = [f"{symbol.lower()}@markPrice{suffix}" for symbol in symbols]
        return await self.market_streams.subscribe(streams)

    async def unsubscribe_mark_price(
        self, symbols: List[str], update_speed: str = "3000ms"
    ) -> Dict[str, Any]:
        """
        Unsubscribe from Mark Price Streams for the given symbols.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).
            update_speed (str): The update speed, either "3000ms" (default) or "1000ms".

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_mark_price(["BTCUSDT", "ETHUSDT"], update_speed="1000ms")
        """
        if update_speed not in ["3000ms", "1000ms"]:
            raise ValueError("update_speed must be either '3000ms' or '1000ms'")

        suffix = "@1s" if update_speed == "1000ms" else ""
        streams = [f"{symbol.lower()}@markPrice{suffix}" for symbol in symbols]
        return await self.market_streams.unsubscribe(streams)

    async def subscribe_all_mark_price(
        self, update_speed: str = "3000ms"
    ) -> Dict[str, Any]:
        """
        Subscribe to Mark Price Streams for all symbols.

        Args:
            update_speed (str): The update speed, either "3000ms" (default) or "1000ms".

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_all_mark_price(update_speed="1000ms")
        """
        if update_speed not in ["3000ms", "1000ms"]:
            raise ValueError("update_speed must be either '3000ms' or '1000ms'")

        suffix = "@1s" if update_speed == "1000ms" else ""
        stream = f"!markPrice@arr{suffix}"
        return await self.market_streams.subscribe([stream])

    async def unsubscribe_all_mark_price(
        self, update_speed: str = "3000ms"
    ) -> Dict[str, Any]:
        """
        Unsubscribe from Mark Price Streams for all symbols.

        Args:
            update_speed (str): The update speed, either "3000ms" (default) or "1000ms".

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_all_mark_price(update_speed="1000ms")
        """
        if update_speed not in ["3000ms", "1000ms"]:
            raise ValueError("update_speed must be either '3000ms' or '1000ms'")

        suffix = "@1s" if update_speed == "1000ms" else ""
        stream = f"!markPrice@arr{suffix}"
        return await self.market_streams.unsubscribe([stream])

    async def subscribe_kline(
        self, symbols: List[str], intervals: List[str]
    ) -> Dict[str, Any]:
        """
        Subscribe to Kline/Candlestick Streams for the given symbols and intervals.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).
            intervals (List[str]): A list of kline/candlestick intervals (e.g., ["1m", "5m", "1h"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_kline(["BTCUSDT", "ETHUSDT"], ["1m", "5m"])
        """
        for interval in intervals:
            if interval not in self.valid_intervals:
                raise ValueError(
                    f"Invalid interval: {interval}. Valid intervals are: {', '.join(self.valid_intervals)}"
                )

        streams = [
            f"{symbol.lower()}@kline_{interval}"
            for symbol in symbols
            for interval in intervals
        ]
        return await self.market_streams.subscribe(streams)

    async def unsubscribe_kline(
        self, symbols: List[str], intervals: List[str]
    ) -> Dict[str, Any]:
        """
        Unsubscribe from Kline/Candlestick Streams for the given symbols and intervals.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).
            intervals (List[str]): A list of kline/candlestick intervals (e.g., ["1m", "5m", "1h"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_kline(["BTCUSDT", "ETHUSDT"], ["1m", "5m"])
        """
        for interval in intervals:
            if interval not in self.valid_intervals:
                raise ValueError(
                    f"Invalid interval: {interval}. Valid intervals are: {', '.join(self.valid_intervals)}"
                )

        streams = [
            f"{symbol.lower()}@kline_{interval}"
            for symbol in symbols
            for interval in intervals
        ]
        return await self.market_streams.unsubscribe(streams)

    async def subscribe_continuous_kline(
        self, pairs: List[str], contract_types: List[str], intervals: List[str]
    ) -> Dict[str, Any]:
        """
        Subscribe to Continuous Contract Kline/Candlestick Streams for the given pairs, contract types, and intervals.

        Args:
            pairs (List[str]): A list of trading pairs (e.g., ["BTCUSDT", "ETHUSDT"]).
            contract_types (List[str]): A list of contract types (e.g., ["perpetual", "current_quarter"]).
            intervals (List[str]): A list of kline/candlestick intervals (e.g., ["1m", "5m", "1h"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_continuous_kline(["BTCUSDT", "ETHUSDT"], ["perpetual"], ["1m", "5m"])
        """
        self._validate_inputs(contract_types, intervals)

        streams = [
            f"{pair.lower()}_{contract_type}@continuousKline_{interval}"
            for pair in pairs
            for contract_type in contract_types
            for interval in intervals
        ]
        return await self.market_streams.subscribe(streams)

    async def unsubscribe_continuous_kline(
        self, pairs: List[str], contract_types: List[str], intervals: List[str]
    ) -> Dict[str, Any]:
        """
        Unsubscribe from Continuous Contract Kline/Candlestick Streams for the given
        pairs, contract types, and intervals.

        Args:
            pairs (List[str]): A list of trading pairs (e.g., ["BTCUSDT", "ETHUSDT"]).
            contract_types (List[str]): A list of contract types (e.g., ["perpetual", "current_quarter"]).
            intervals (List[str]): A list of kline/candlestick intervals (e.g., ["1m", "5m", "1h"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_continuous_kline(["BTCUSDT", "ETHUSDT"], ["perpetual"], ["1m", "5m"])
        """
        self._validate_inputs(contract_types, intervals)

        streams = [
            f"{pair.lower()}_{contract_type}@continuousKline_{interval}"
            for pair in pairs
            for contract_type in contract_types
            for interval in intervals
        ]
        return await self.market_streams.unsubscribe(streams)

    async def subscribe_mini_ticker(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Subscribe to Individual Symbol Mini Ticker Streams for the given symbols.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_mini_ticker(["BTCUSDT", "ETHUSDT"])
        """
        streams = [f"{symbol.lower()}@miniTicker" for symbol in symbols]
        return await self.market_streams.subscribe(streams)

    async def unsubscribe_mini_ticker(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Unsubscribe from Individual Symbol Mini Ticker Streams for the given symbols.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_mini_ticker(["BTCUSDT", "ETHUSDT"])
        """
        streams = [f"{symbol.lower()}@miniTicker" for symbol in symbols]
        return await self.market_streams.unsubscribe(streams)

    async def subscribe_all_market_tickers(self) -> Dict[str, Any]:
        """
        Subscribe to the All Market Tickers Stream.

        This stream provides 24hr rolling window ticker statistics for all symbols.
        Note that only tickers that have changed will be present in the array.

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_all_market_tickers()
        """
        stream = "!ticker@arr"
        return await self.market_streams.subscribe([stream])

    async def unsubscribe_all_market_tickers(self) -> Dict[str, Any]:
        """
        Unsubscribe from the All Market Tickers Stream.

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_all_market_tickers()
        """
        stream = "!ticker@arr"
        return await self.market_streams.unsubscribe([stream])

    async def subscribe_symbol_ticker(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Subscribe to Individual Symbol Ticker Streams for the given symbols.

        This stream provides 24hr rolling window ticker statistics for the specified symbols.
        These are NOT the statistics of the UTC day, but a 24hr rolling window from requestTime to 24hrs before.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_symbol_ticker(["BTCUSDT", "ETHUSDT"])
        """
        streams = [f"{symbol.lower()}@ticker" for symbol in symbols]
        return await self.market_streams.subscribe(streams)

    async def unsubscribe_symbol_ticker(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Unsubscribe from Individual Symbol Ticker Streams for the given symbols.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_symbol_ticker(["BTCUSDT", "ETHUSDT"])
        """
        streams = [f"{symbol.lower()}@ticker" for symbol in symbols]
        return await self.market_streams.unsubscribe(streams)

    async def subscribe_all_market_mini_tickers(self) -> Dict[str, Any]:
        """
        Subscribe to the All Market Mini Tickers Stream.

        This stream provides 24hr rolling window mini-ticker statistics for all symbols.
        These are NOT the statistics of the UTC day, but a 24hr rolling window from requestTime to 24hrs before.
        Note that only tickers that have changed will be present in the array.

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_all_market_mini_tickers()
        """
        stream = "!miniTicker@arr"
        return await self.market_streams.subscribe([stream])

    async def unsubscribe_all_market_mini_tickers(self) -> Dict[str, Any]:
        """
        Unsubscribe from the All Market Mini Tickers Stream.

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_all_market_mini_tickers()
        """
        stream = "!miniTicker@arr"
        return await self.market_streams.unsubscribe([stream])

    async def subscribe_book_ticker(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Subscribe to Individual Symbol Book Ticker Streams for the given symbols.

        This stream pushes any update to the best bid or ask's price or quantity in real-time for the specified symbols.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_book_ticker(["BTCUSDT", "ETHUSDT"])
        """
        streams = [f"{symbol.lower()}@bookTicker" for symbol in symbols]
        return await self.market_streams.subscribe(streams)

    async def unsubscribe_book_ticker(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Unsubscribe from Individual Symbol Book Ticker Streams for the given symbols.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_book_ticker(["BTCUSDT", "ETHUSDT"])
        """
        streams = [f"{symbol.lower()}@bookTicker" for symbol in symbols]
        return await self.market_streams.unsubscribe(streams)

    async def subscribe_all_book_tickers(self) -> Dict[str, Any]:
        """
        Subscribe to the All Book Tickers Stream.

        This stream pushes any update to the best bid or ask's price or quantity in real-time for all symbols.

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_all_book_tickers()
        """
        stream = "!bookTicker"
        return await self.market_streams.subscribe([stream])

    async def unsubscribe_all_book_tickers(self) -> Dict[str, Any]:
        """
        Unsubscribe from the All Book Tickers Stream.

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_all_book_tickers()
        """
        stream = "!bookTicker"
        return await self.market_streams.unsubscribe([stream])

    async def subscribe_liquidation_order(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Subscribe to Liquidation Order Snapshot Streams for the given symbols.

        This stream pushes force liquidation order information for specific symbols.
        For each symbol, only the latest liquidation order within 1000ms will be pushed as the snapshot.
        If no liquidation happens in the interval of 1000ms, no stream will be pushed.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_liquidation_order(["BTCUSDT", "ETHUSDT"])
        """
        streams = [f"{symbol.lower()}@forceOrder" for symbol in symbols]
        return await self.market_streams.subscribe(streams)

    async def unsubscribe_liquidation_order(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Unsubscribe from Liquidation Order Snapshot Streams for the given symbols.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_liquidation_order(["BTCUSDT", "ETHUSDT"])
        """
        streams = [f"{symbol.lower()}@forceOrder" for symbol in symbols]
        return await self.market_streams.unsubscribe(streams)

    async def subscribe_all_liquidation_orders(self) -> Dict[str, Any]:
        """
        Subscribe to the All Market Liquidation Order Streams.

        This stream pushes force liquidation order information for all symbols in the market.
        For each symbol, only the latest liquidation order within 1000ms will be pushed as the snapshot.
        If no liquidation happens in the interval of 1000ms, no stream will be pushed.

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_all_liquidation_orders()
        """
        stream = "!forceOrder@arr"
        return await self.market_streams.subscribe([stream])

    async def unsubscribe_all_liquidation_orders(self) -> Dict[str, Any]:
        """
        Unsubscribe from the All Market Liquidation Order Streams.

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_all_liquidation_orders()
        """
        stream = "!forceOrder@arr"
        return await self.market_streams.unsubscribe([stream])

    async def subscribe_partial_book_depth(
        self, symbols: List[str], levels: int, update_speed: int = 250
    ) -> Dict[str, Any]:
        """
        Subscribe to Partial Book Depth Streams for the given symbols.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).
            levels (int): The number of levels to be included in the partial book depth.
            Valid values are 5, 10, or 20.
            update_speed (int, optional): The update speed in milliseconds.
            Valid values are 250, 500, or 100. Defaults to 250.

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Raises:
            ValueError: If invalid levels or update_speed are provided.

        Example:
            >>> await market_service.subscribe_partial_book_depth(["BTCUSDT", "ETHUSDT"], levels=10, update_speed=500)
        """
        if levels not in self.valid_depth_levels:
            raise ValueError(
                f"Invalid levels. Must be one of {self.valid_depth_levels}"
            )

        if update_speed not in self.valid_update_speeds:
            raise ValueError(
                f"Invalid update_speed. Must be one of {self.valid_update_speeds}"
            )

        speed_suffix = "" if update_speed == 250 else f"@{update_speed}ms"
        streams = [
            f"{symbol.lower()}@depth{levels}{speed_suffix}" for symbol in symbols
        ]
        return await self.market_streams.subscribe(streams)

    async def unsubscribe_partial_book_depth(
        self, symbols: List[str], levels: int, update_speed: int = 250
    ) -> Dict[str, Any]:
        """
        Unsubscribe from Partial Book Depth Streams for the given symbols.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).
            levels (int): The number of levels included in the partial book depth.
            Valid values are 5, 10, or 20.
            update_speed (int, optional): The update speed in milliseconds.
            Valid values are 250, 500, or 100. Defaults to 250.

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Raises:
            ValueError: If invalid levels or update_speed are provided.

        Example:
            >>> await market_service.unsubscribe_partial_book_depth(["BTCUSDT", "ETHUSDT"], levels=10, update_speed=500)
        """
        if levels not in self.valid_depth_levels:
            raise ValueError(
                f"Invalid levels. Must be one of {self.valid_depth_levels}"
            )

        if update_speed not in self.valid_update_speeds:
            raise ValueError(
                f"Invalid update_speed. Must be one of {self.valid_update_speeds}"
            )

        speed_suffix = "" if update_speed == 250 else f"@{update_speed}ms"
        streams = [
            f"{symbol.lower()}@depth{levels}{speed_suffix}" for symbol in symbols
        ]
        return await self.market_streams.unsubscribe(streams)

    async def subscribe_diff_book_depth(
        self, symbols: List[str], update_speed: int = 250
    ) -> Dict[str, Any]:
        """
        Subscribe to Diff. Book Depth Streams for the given symbols.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).
            update_speed (int, optional): The update speed in milliseconds.
            valid values are 250, 500, or 100. Defaults to 250.

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Raises:
            ValueError: If an invalid update_speed is provided.

        Example:
            >>> await market_service.subscribe_diff_book_depth(["BTCUSDT", "ETHUSDT"], update_speed=500)
        """
        if update_speed not in self.valid_update_speeds:
            raise ValueError(
                f"Invalid update_speed. Must be one of {self.valid_update_speeds}"
            )

        speed_suffix = "" if update_speed == 250 else f"@{update_speed}ms"
        streams = [f"{symbol.lower()}@depth{speed_suffix}" for symbol in symbols]
        return await self.market_streams.subscribe(streams)

    async def unsubscribe_diff_book_depth(
        self, symbols: List[str], update_speed: int = 250
    ) -> Dict[str, Any]:
        """
        Unsubscribe from Diff. Book Depth Streams for the given symbols.

        Args:
            symbols (List[str]): A list of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"]).
            update_speed (int, optional): The update speed in milliseconds.
            Valid values are 250, 500, or 100. Defaults to 250.

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Raises:
            ValueError: If an invalid update_speed is provided.

        Example:
            >>> await market_service.unsubscribe_diff_book_depth(["BTCUSDT", "ETHUSDT"], update_speed=500)
        """
        if update_speed not in self.valid_update_speeds:
            raise ValueError(
                f"Invalid update_speed. Must be one of {self.valid_update_speeds}"
            )

        speed_suffix = "" if update_speed == 250 else f"@{update_speed}ms"
        streams = [f"{symbol.lower()}@depth{speed_suffix}" for symbol in symbols]
        return await self.market_streams.unsubscribe(streams)

    async def subscribe_composite_index(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Subscribe to Composite Index Symbol Information Streams for the given symbols.

        This stream provides composite index information for index symbols, pushed every second.

        Args:
            symbols (List[str]): A list of index symbols (e.g., ["DEFIUSDT", "NFTUSDT"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_composite_index(["DEFIUSDT", "NFTUSDT"])
        """
        streams = [f"{symbol.lower()}@compositeIndex" for symbol in symbols]
        return await self.market_streams.subscribe(streams)

    async def unsubscribe_composite_index(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Unsubscribe from Composite Index Symbol Information Streams for the given symbols.

        Args:
            symbols (List[str]): A list of index symbols (e.g., ["DEFIUSDT", "NFTUSDT"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_composite_index(["DEFIUSDT", "NFTUSDT"])
        """
        streams = [f"{symbol.lower()}@compositeIndex" for symbol in symbols]
        return await self.market_streams.unsubscribe(streams)

    async def subscribe_contract_info(self) -> Dict[str, Any]:
        """
        Subscribe to the Contract Info Stream.

        This stream pushes updates when contract info changes, including listings,
        settlements, and contract bracket updates. The 'bks' field is only included
        when a bracket is updated.

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_contract_info()
        """
        stream = "!contractInfo"
        return await self.market_streams.subscribe([stream])

    async def unsubscribe_contract_info(self) -> Dict[str, Any]:
        """
        Unsubscribe from the Contract Info Stream.

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_contract_info()
        """
        stream = "!contractInfo"
        return await self.market_streams.unsubscribe([stream])

    async def subscribe_asset_index_array(self) -> Dict[str, Any]:
        """
        Subscribe to the Multi-Assets Mode Asset Index array stream.

        This stream provides asset index information for all assets in multi-assets mode,
        updated every second.

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_asset_index_array()
        """
        stream = "!assetIndex@arr"
        return await self.market_streams.subscribe([stream])

    async def unsubscribe_asset_index_array(self) -> Dict[str, Any]:
        """
        Unsubscribe from the Multi-Assets Mode Asset Index array stream.

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_asset_index_array()
        """
        stream = "!assetIndex@arr"
        return await self.market_streams.unsubscribe([stream])

    async def subscribe_asset_index(self, asset_symbols: List[str]) -> Dict[str, Any]:
        """
        Subscribe to the Multi-Assets Mode Asset Index stream for specific assets.

        This stream provides asset index information for the specified assets in
        multi-assets mode, updated every second.

        Args:
            asset_symbols (List[str]): A list of asset symbols (e.g., ["BTC", "ETH"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.subscribe method.

        Example:
            >>> await market_service.subscribe_asset_index(["BTC", "ETH"])
        """
        streams = [f"{symbol.lower()}@assetIndex" for symbol in asset_symbols]
        return await self.market_streams.subscribe(streams)

    async def unsubscribe_asset_index(self, asset_symbols: List[str]) -> Dict[str, Any]:
        """
        Unsubscribe from the Multi-Assets Mode Asset Index stream for specific assets.

        Args:
            asset_symbols (List[str]): A list of asset symbols (e.g., ["BTC", "ETH"]).

        Returns:
            Dict[str, Any]: The response from the MarketStreams.unsubscribe method.

        Example:
            >>> await market_service.unsubscribe_asset_index(["BTC", "ETH"])
        """
        streams = [f"{symbol.lower()}@assetIndex" for symbol in asset_symbols]
        return await self.market_streams.unsubscribe(streams)

    def _validate_inputs(self, contract_types: List[str], intervals: List[str]):
        """
        Validate the input contract types and intervals.

        Args:
            contract_types (List[str]): A list of contract types to validate.
            intervals (List[str]): A list of intervals to validate.

        Raises:
            ValueError: If any of the inputs are invalid.
        """
        for contract_type in contract_types:
            if contract_type not in self.valid_contract_types:
                raise ValueError(
                    f"Invalid contract type: {contract_type}. Valid types are: {', '.join(self.valid_contract_types)}"
                )

        for interval in intervals:
            if interval not in self.valid_intervals:
                raise ValueError(
                    f"Invalid interval: {interval}. Valid intervals are: {', '.join(self.valid_intervals)}"
                )

    async def list_subscriptions(self) -> List[str]:
        return await self.market_streams.list_subscriptions()

    async def set_property(self, name: str, value: Any) -> Dict[str, Any]:
        return await self.market_streams.set_property(name, value)

    async def get_property(self, name: str) -> Any:
        return await self.market_streams.get_property(name)
