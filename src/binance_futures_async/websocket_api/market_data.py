from typing import (
    Any,
    Dict,
    Optional,
)


class MarketData:
    def get_depth(self, symbol: str, limit: Optional[int] = None) -> Dict[str, Any]:
        params = {"symbol": symbol}
        if limit is not None:
            params["limit"] = limit
        return params

    def get_ticker_price(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if symbol:
            params["symbol"] = symbol
        return params

    def get_ticker_book(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if symbol:
            params["symbol"] = symbol
        return params
