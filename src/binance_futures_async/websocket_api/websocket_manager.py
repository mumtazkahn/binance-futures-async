# websocket_manager.py

import asyncio
import json
import time
from decimal import Decimal
from typing import (
    Any,
    Dict,
    Optional,
)

import aiohttp

from ..exceptions import (
    ConnectionError,
    RequestError,
)
from ..utils import generate_request_id


class ConnectionState:
    DISCONNECTED = "DISCONNECTED"
    CONNECTED = "CONNECTED"
    AUTHENTICATED = "AUTHENTICATED"


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)


class WebSocketManager:
    def __init__(self, base_url: str, config: Dict[str, Any]):
        self.base_url = base_url
        self.config = config
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.connection_state = ConnectionState.DISCONNECTED
        self.connection_lock = asyncio.Lock()
        self.last_ping_time = 0
        self.response_futures: Dict[str, asyncio.Future] = {}

    async def connect(self):
        async with self.connection_lock:
            if self.connection_state != ConnectionState.DISCONNECTED:
                return

            try:
                await self._connect()
                self.connection_state = ConnectionState.CONNECTED
                asyncio.create_task(self._check_connection_loop())
                asyncio.create_task(self._handle_messages())
            except Exception as e:
                self.connection_state = ConnectionState.DISCONNECTED
                raise ConnectionError(f"Failed to connect: {str(e)}")

    async def _connect(self):
        if self.session and not self.session.closed:
            await self.session.close()

        self.session = aiohttp.ClientSession()
        try:
            self.ws = await asyncio.wait_for(
                self.session.ws_connect(
                    f"{self.base_url}?returnRateLimits={str(self.config['return_rate_limits']).lower()}"
                ),
                timeout=self.config["connection_timeout"],
            )
            self.last_ping_time = time.time()
        except Exception as e:
            if self.session:
                await self.session.close()
                self.session = None
            raise ConnectionError(f"Connection failed: {str(e)}")

    async def close(self):
        async with self.connection_lock:
            self.connection_state = ConnectionState.DISCONNECTED
            if self.ws:
                await self.ws.close()
            if self.session and not self.session.closed:
                await self.session.close()
            self.ws = None
            self.session = None

    async def _check_connection_loop(self):
        while True:
            if self.connection_state == ConnectionState.DISCONNECTED:
                await asyncio.sleep(5)
                continue

            await asyncio.sleep(5)
            try:
                if (self.ws and self.ws.closed) or (
                    time.time() - self.last_ping_time
                    > self.config["ping_interval"] + 10
                ):
                    await self._reconnect()
            except Exception:
                await self.close()

    async def _reconnect(self):
        async with self.connection_lock:
            self.connection_state = ConnectionState.DISCONNECTED
            attempts = 0
            delay = self.config["reconnect_delay"]

            while attempts < self.config["max_reconnect_attempts"]:
                try:
                    await self._connect()
                    self.connection_state = ConnectionState.CONNECTED
                    return
                except ConnectionError:
                    attempts += 1
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, self.config["max_reconnect_delay"])
            raise

    async def _handle_ping(self, payload):
        if self.ws and not self.ws.closed:
            await self.ws.pong(payload)
        self.last_ping_time = time.time()

    async def send_request(
        self,
        method: str,
        params: Dict[str, Any] = None,
        wait_for_response: bool = True,
    ) -> Dict[str, Any]:
        if self.connection_state == ConnectionState.DISCONNECTED:
            raise ConnectionError("WebSocket is disconnected")

        request_id = generate_request_id()
        request = {"id": request_id, "method": method, "params": params or {}}

        try:
            await asyncio.wait_for(
                self.ws.send_json(
                    request,
                    dumps=lambda obj: json.dumps(obj, cls=DecimalEncoder),
                ),
                timeout=self.config["request_timeout"],
            )
        except Exception as e:
            raise RequestError(f"Failed to send request: {str(e)}")

        if not wait_for_response:
            return {"status": "sent"}

        future = asyncio.Future()
        self.response_futures[request_id] = future

        try:
            response = await asyncio.wait_for(
                future, timeout=self.config["request_timeout"]
            )
            return response
        except asyncio.TimeoutError:
            del self.response_futures[request_id]
            raise RequestError("Response timed out")

    async def _handle_messages(self):
        while True:
            if self.connection_state == ConnectionState.DISCONNECTED:
                await asyncio.sleep(1)
                continue

            try:
                msg = await self.ws.receive()
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if "id" in data:
                        future = self.response_futures.pop(data["id"], None)
                        if future and not future.done():
                            future.set_result(data)
                elif msg.type == aiohttp.WSMsgType.PING:
                    await self._handle_ping(msg.data)
                elif msg.type in (
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.ERROR,
                ):
                    raise ConnectionError(f"WebSocket connection {msg.type.name}")
            except Exception:
                await asyncio.sleep(1)

    def set_state(self, state: str):
        self.connection_state = state

    def get_state(self) -> str:
        return self.connection_state
