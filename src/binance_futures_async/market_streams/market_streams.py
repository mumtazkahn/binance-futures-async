import asyncio
import json
import time
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
)

import aiohttp

from ..exceptions import (
    ConnectionError,
    RequestError,
)


class MarketStreams:
    def __init__(
        self,
        base_url: str,
        message_handler: Callable[[Dict[str, Any]], None],
        config: Dict[str, Any],
    ):
        if not callable(message_handler):
            raise ValueError("message_handler must be a callable")

        self.base_url = base_url
        self.message_handler = message_handler
        self.config = config

        # WebSocket and Session
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.session: Optional[aiohttp.ClientSession] = None

        # State management
        self.subscriptions: set = set()
        self.combined: bool = False
        self.message_id: int = 0
        self._is_connected = False
        self.connection_lock = asyncio.Lock()
        self.last_ping_time = 0

        # Background tasks
        self.health_check_task: Optional[asyncio.Task] = None
        self.message_processor_task: Optional[asyncio.Task] = None

        # Message handling
        self.message_queue = asyncio.Queue()
        self.response_futures: Dict[int, asyncio.Future] = {}

        self._fatal_error = False

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    async def connect(self):
        """Initialize and start the market stream connection."""
        async with self.connection_lock:
            if self._is_connected:
                return

            try:
                await self._establish_connection()
                self._start_background_tasks()
                self._is_connected = True
            except Exception as e:
                await self._cleanup()
                raise ConnectionError(f"Failed to start stream: {str(e)}")

    async def close(self):
        """Stop the market stream and cleanup resources."""
        async with self.connection_lock:
            if not self._is_connected:
                return
            await self._cleanup()

    async def _establish_connection(self):
        """Establish WebSocket connection."""
        if self.session and not self.session.closed:
            await self.session.close()

        self.session = aiohttp.ClientSession()
        try:
            self.ws = await asyncio.wait_for(
                self.session.ws_connect(f"{self.base_url}/ws"),
                timeout=self.config["connection_timeout"],
            )
            asyncio.create_task(self._receive_messages())
            self.last_ping_time = time.time()
        except Exception as e:
            await self._cleanup()
            raise ConnectionError(f"WebSocket connection failed: {str(e)}")

    def _start_background_tasks(self):
        """Start background tasks for health checking and message processing."""
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        self.message_processor_task = asyncio.create_task(self._process_messages())

    async def _cleanup(self):
        """Clean up all resources and reset state."""
        self._is_connected = False

        for task in [self.health_check_task, self.message_processor_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        if self.ws:
            await self.ws.close()

        if self.session and not self.session.closed:
            await self.session.close()

        self.ws = None
        self.session = None

        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
                self.message_queue.task_done()
            except asyncio.QueueEmpty:
                break

    async def _health_check_loop(self):
        """Periodic health check and connection monitoring."""
        while True:
            try:
                await asyncio.sleep(5)
                if not self._is_connected or not self.ws or self.ws.closed:
                    await self._reconnect()
                elif (
                    time.time() - self.last_ping_time
                    > self.config["ping_interval"] + 10
                ):
                    await self._reconnect()
            except asyncio.CancelledError:
                break
            except Exception:
                if not self._fatal_error:  # Only try reconnect if not fatally failed
                    await self._reconnect()
                else:
                    break  # Exit loop if we've had a fatal error

    async def _reconnect(self):
        """Handle reconnection with exponential backoff."""
        async with self.connection_lock:
            if self._fatal_error:
                return  # Don't attempt reconnect if we've had a fatal error

            await self._cleanup()
            retry_count = 0
            delay = self.config["reconnect_delay"]

            while retry_count < self.config["max_reconnect_attempts"]:
                try:
                    await self._establish_connection()
                    self._start_background_tasks()
                    self._is_connected = True
                    await self._resubscribe()
                    return
                except Exception:
                    retry_count += 1
                    if retry_count < self.config["max_reconnect_attempts"]:
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, self.config["max_reconnect_delay"])

            # Mark as fatally failed before cleanup and raise
            self._fatal_error = True
            await self._cleanup()
            raise ConnectionError("Failed to reconnect after maximum retries")

    async def _receive_messages(self):
        """Handle incoming WebSocket messages."""
        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self.message_queue.put(json.loads(msg.data))
                elif msg.type in (
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.ERROR,
                ):
                    await self._reconnect()
                    break
        except Exception:
            await self._reconnect()

    async def _process_messages(self):
        """Process messages from the message queue."""
        while True:
            try:
                message = await self.message_queue.get()
                if "id" in message:
                    future = self.response_futures.pop(message["id"], None)
                    if future and not future.done():
                        future.set_result(message)
                elif message.get("e") == "ping":
                    await self._handle_ping(message)
                else:
                    await asyncio.to_thread(self.message_handler, message)
                self.message_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception:
                continue

    async def _handle_ping(self, message):
        if self.ws and not self.ws.closed:
            await self.ws.pong()
        self.last_ping_time = time.time()

    async def send_request(
        self, method: str, params: List[Any] = None
    ) -> Dict[str, Any]:
        """Send a request to the WebSocket server and await response."""
        if not self._is_connected:
            raise ConnectionError("WebSocket is not connected")

        self.message_id += 1
        request = {
            "method": method,
            "params": params or [],
            "id": self.message_id,
        }

        future = asyncio.Future()
        self.response_futures[self.message_id] = future

        try:
            await self.ws.send_json(request)
            return await asyncio.wait_for(
                future, timeout=self.config["request_timeout"]
            )
        except asyncio.TimeoutError:
            del self.response_futures[self.message_id]
            raise RequestError("Request timed out")
        except Exception as e:
            del self.response_futures[self.message_id]
            raise RequestError(f"Failed to send request: {str(e)}")

    # Subscription methods remain unchanged
    async def subscribe(self, streams: List[str]):
        params = [stream for stream in streams if stream not in self.subscriptions]
        if not params:
            return
        response = await self.send_request("SUBSCRIBE", params)
        if response.get("result") is None:
            self.subscriptions.update(params)
        else:
            raise RequestError(f"Failed to subscribe: {response}")
        return response

    async def unsubscribe(self, streams: List[str]):
        params = [stream for stream in streams if stream in self.subscriptions]
        if not params:
            return
        response = await self.send_request("UNSUBSCRIBE", params)
        if response.get("result") is None:
            self.subscriptions.difference_update(params)
        else:
            raise RequestError(f"Failed to unsubscribe: {response}")
        return response

    async def _resubscribe(self):
        if self.subscriptions:
            await self.subscribe(list(self.subscriptions))

    async def list_subscriptions(self):
        return list(self.subscriptions)

    async def set_property(self, name: str, value: Any):
        response = await self.send_request("SET_PROPERTY", [name, value])
        if response.get("result") is None:
            if name == "combined":
                self.combined = value
        else:
            raise RequestError(f"Failed to set property: {response}")
        return response

    async def get_property(self, name: str):
        response = await self.send_request("GET_PROPERTY", [name])
        return response.get("result")
