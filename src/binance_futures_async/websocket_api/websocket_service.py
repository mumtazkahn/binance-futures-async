# websocket_service.py

import time
from typing import (
    Any,
    Dict,
    Optional,
)

from ..auth.auth_factory import create_auth
from ..exceptions import (
    AuthenticationError,
    BinanceWebSocketError,
    ConnectionError,
    RequestError,
)
from .account_info import AccountInfo
from .market_data import MarketData
from .order_preparation import OrderPreparation
from .websocket_manager import (
    ConnectionState,
    WebSocketManager,
)


class WebSocketService:
    def __init__(
        self,
        api_key: str,
        private_key_path: str,
        enable_validation: bool = False,
        config: Dict[str, Any] = None,
    ):
        self.auth, self.key_type = create_auth(api_key, private_key_path)
        self.ws_manager = WebSocketManager(
            "wss://ws-fapi.binance.com/ws-fapi/v1", config
        )
        self.account_info = AccountInfo()
        self.order_preparation = OrderPreparation(enable_validation)
        self.market_data = MarketData()

    async def connect(self):
        try:
            await self.ws_manager.connect()
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {str(e)}")

    async def close(self):
        await self.ws_manager.close()

    async def login(self, wait_for_response: bool = True):
        if self.key_type != "Ed25519":
            raise AuthenticationError(
                "Login method is only supported with Ed25519 keys"
            )

        try:
            result = await self._send_request(
                "session.logon", wait_for_response=wait_for_response
            )
            if wait_for_response and result.get("status") == 200:
                self.ws_manager.set_state(ConnectionState.AUTHENTICATED)
            return result
        except Exception as e:
            raise AuthenticationError(f"Login failed: {str(e)}")

    async def logout(self, wait_for_response: bool = True):
        if self.ws_manager.get_state() != ConnectionState.AUTHENTICATED:
            return

        try:
            result = await self._send_request(
                "session.logout", wait_for_response=wait_for_response
            )
            if wait_for_response and result.get("status") == 200:
                self.ws_manager.set_state(ConnectionState.CONNECTED)
            return result
        except Exception as e:
            raise RequestError(f"Logout failed: {str(e)}")

    def generate_timestamp(self) -> int:
        return int(time.time() * 1000)

    async def _send_request(
        self,
        method: str,
        params: Dict[str, Any] = None,
        wait_for_response: bool = True,
    ) -> Dict[str, Any]:
        params = params or {}

        # Add authentication for secured endpoints
        if method not in [
            "session.status",
            "session.logout",
            "depth",
            "ticker.price",
            "ticker.book",
        ]:
            params["timestamp"] = self.generate_timestamp()
            if self.ws_manager.get_state() != ConnectionState.AUTHENTICATED:
                params["apiKey"] = self.auth.api_key
                params["signature"] = await self.auth.sign(params)

        try:
            return await self.ws_manager.send_request(method, params, wait_for_response)
        except Exception as e:
            if isinstance(e, (ConnectionError, RequestError)):
                raise
            raise BinanceWebSocketError(f"Request failed: {str(e)}")

    # Market Data Methods
    async def get_depth(
        self,
        symbol: str,
        limit: Optional[int] = None,
        wait_for_response: bool = True,
    ) -> Dict[str, Any]:
        return await self._send_request(
            "depth",
            self.market_data.get_depth(symbol, limit),
            wait_for_response,
        )

    async def get_ticker_price(
        self, symbol: Optional[str] = None, wait_for_response: bool = True
    ) -> Dict[str, Any]:
        return await self._send_request(
            "ticker.price",
            self.market_data.get_ticker_price(symbol),
            wait_for_response,
        )

    async def get_ticker_book(
        self, symbol: Optional[str] = None, wait_for_response: bool = True
    ) -> Dict[str, Any]:
        return await self._send_request(
            "ticker.book",
            self.market_data.get_ticker_book(symbol),
            wait_for_response,
        )

    # Account Methods
    async def get_position_info(
        self, symbol: str = None, wait_for_response: bool = True
    ) -> Dict[str, Any]:
        return await self._send_request(
            "v2/account.position",
            self.account_info.get_position_info(symbol),
            wait_for_response,
        )

    async def get_account_balance(
        self, wait_for_response: bool = True
    ) -> Dict[str, Any]:
        return await self._send_request(
            "v2/account.balance",
            self.account_info.get_account_balance(),
            wait_for_response,
        )

    async def get_account_status(
        self, wait_for_response: bool = True
    ) -> Dict[str, Any]:
        return await self._send_request(
            "v2/account.status",
            self.account_info.get_account_status(),
            wait_for_response,
        )

    # Order Methods
    async def place_limit_order(
        self, wait_for_response: bool = True, **kwargs
    ) -> Dict[str, Any]:
        return await self._send_request(
            "order.place",
            self.order_preparation.place_limit_order(**kwargs),
            wait_for_response,
        )

    async def place_market_order(
        self, wait_for_response: bool = True, **kwargs
    ) -> Dict[str, Any]:
        return await self._send_request(
            "order.place",
            self.order_preparation.place_market_order(**kwargs),
            wait_for_response,
        )

    async def place_stop_order(
        self, wait_for_response: bool = True, **kwargs
    ) -> Dict[str, Any]:
        return await self._send_request(
            "order.place",
            self.order_preparation.place_stop_order(**kwargs),
            wait_for_response,
        )

    async def place_stop_market_order(
        self, wait_for_response: bool = True, **kwargs
    ) -> Dict[str, Any]:
        return await self._send_request(
            "order.place",
            self.order_preparation.place_stop_market_order(**kwargs),
            wait_for_response,
        )

    async def place_take_profit_order(
        self, wait_for_response: bool = True, **kwargs
    ) -> Dict[str, Any]:
        return await self._send_request(
            "order.place",
            self.order_preparation.place_take_profit_order(**kwargs),
            wait_for_response,
        )

    async def place_take_profit_market_order(
        self, wait_for_response: bool = True, **kwargs
    ) -> Dict[str, Any]:
        return await self._send_request(
            "order.place",
            self.order_preparation.place_take_profit_market_order(**kwargs),
            wait_for_response,
        )

    async def place_trailing_stop_market_order(
        self, wait_for_response: bool = True, **kwargs
    ) -> Dict[str, Any]:
        return await self._send_request(
            "order.place",
            self.order_preparation.place_trailing_stop_market_order(**kwargs),
            wait_for_response,
        )
