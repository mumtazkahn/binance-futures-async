from typing import (
    Any,
    Callable,
    Dict,
)

from .market_streams.market_service import MarketService
from .user_data_streams.user_data_stream_api import UserDataStreamAPI
from .websocket_api.websocket_service import WebSocketService

DEFAULT_WEBSOCKET_CONFIG = {
    "return_rate_limits": True,
    "connection_timeout": 30,
    "request_timeout": 30,
    "ping_interval": 180,
    "reconnect_delay": 5,
    "max_reconnect_delay": 300,
    "max_reconnect_attempts": 5,
}

DEFAULT_USER_STREAM_CONFIG = {
    "connection_timeout": 30,
    "request_timeout": 30,
    "ping_interval": 3300,  # 55 minutes
    "reconnect_delay": 5,
    "max_reconnect_delay": 300,
    "max_reconnect_attempts": 5,
    "health_check_interval": 60,  # 1 minute
}

DEFAULT_MARKET_STREAM_CONFIG = {
    "connection_timeout": 30,
    "request_timeout": 30,
    "ping_interval": 180,
    "reconnect_delay": 5,
    "max_reconnect_delay": 300,
    "max_reconnect_attempts": 5,
}


class BinanceClient:
    def __init__(self):
        self._websocket_service = None
        self._user_data_stream = None
        self._market_service = None

    async def websocket_service(
        self,
        api_key: str,
        private_key_path: str,
        enable_validation: bool = False,
        config: Dict[str, Any] = None,
    ) -> WebSocketService:
        """Initialize and return the WebSocket service."""
        if not self._websocket_service:
            service_config = {**DEFAULT_WEBSOCKET_CONFIG, **(config or {})}
            self._websocket_service = WebSocketService(
                api_key=api_key,
                private_key_path=private_key_path,
                enable_validation=enable_validation,
                config=service_config,
            )
            await self._websocket_service.connect()
        return self._websocket_service

    async def user_stream(
        self,
        api_key: str,
        message_handler: Callable[[Dict[str, Any]], None],
        config: Dict[str, Any] = None,
    ) -> UserDataStreamAPI:
        """Initialize and return the user data stream API."""
        if not self._user_data_stream:
            stream_config = {**DEFAULT_USER_STREAM_CONFIG, **(config or {})}
            self._user_data_stream = UserDataStreamAPI(
                api_key=api_key,
                message_handler=message_handler,
                config=stream_config,
            )
            await self._user_data_stream.start()
        return self._user_data_stream

    async def market_service(
        self,
        message_handler: Callable[[Dict[str, Any]], None],
        config: Dict[str, Any] = None,
    ) -> MarketService:
        """Initialize and return the market service."""
        if not self._market_service:
            service_config = {**DEFAULT_MARKET_STREAM_CONFIG, **(config or {})}
            self._market_service = MarketService(
                base_url="wss://fstream.binance.com",
                message_handler=message_handler,
                config=service_config,
            )
            await self._market_service.connect()
        return self._market_service
