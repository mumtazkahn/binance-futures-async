import asyncio
import json
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
)

import aiohttp

from ..exceptions import (
    ConnectionError,
    UserStreamError,
)


class UserDataStreamInfrastructure:
    """Infrastructure layer for managing WebSocket connections to Binance user data streams."""

    def __init__(
        self,
        api_key: str,
        message_handler: Callable[[Dict[str, Any]], None],
        config: Dict[str, Any],
    ):
        self._api_key = api_key
        self._message_handler = message_handler
        self._config = config
        self._listen_key: Optional[str] = None
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._is_connected = False
        self._message_id = 0
        self._connection_lock = asyncio.Lock()
        self._message_queue = asyncio.Queue()
        self._health_check_task: Optional[asyncio.Task] = None
        self._message_processor_task: Optional[asyncio.Task] = None
        self._fatal_error = True

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def listen_key(self) -> Optional[str]:
        return self._listen_key

    async def start(self) -> None:
        """Initialize and start the user data stream connection."""
        async with self._connection_lock:
            if self._is_connected:
                return

            try:
                await self._initialize_listen_key()
                await self._establish_connection()
                self._start_background_tasks()
                self._is_connected = True
            except Exception as e:
                await self._cleanup()
                raise ConnectionError(f"Failed to start stream: {str(e)}")

    async def stop(self) -> None:
        """Stop the user data stream and cleanup resources."""
        async with self._connection_lock:
            if not self._is_connected:
                return
            await self._cleanup()

    async def _initialize_listen_key(self) -> None:
        """Get a listen key from Binance."""
        self._session = aiohttp.ClientSession()
        try:
            ws = await self._session.ws_connect(
                "wss://ws-fapi.binance.com/ws-fapi/v1",
                timeout=self._config["connection_timeout"],
            )

            await ws.send_json(
                {
                    "id": self._get_next_id(),
                    "method": "userDataStream.start",
                    "params": {"apiKey": self._api_key},
                }
            )

            response = await ws.receive_json(timeout=self._config["request_timeout"])
            await ws.close()

            if response.get("status") == 200:
                self._listen_key = response["result"]["listenKey"]
            else:
                raise UserStreamError(f"Failed to get listen key: {response}")
        except Exception as e:
            await self._cleanup()
            raise ConnectionError(f"Listen key initialization failed: {str(e)}")

    async def _establish_connection(self) -> None:
        """Establish WebSocket connection using the listen key."""
        try:
            self._ws = await self._session.ws_connect(
                f"wss://fstream.binance.com/ws/{self._listen_key}",
                timeout=self._config["connection_timeout"],
            )
            asyncio.create_task(self._handle_messages())
        except Exception as e:
            raise ConnectionError(f"WebSocket connection failed: {str(e)}")

    def _start_background_tasks(self) -> None:
        """Start background tasks for health checking and message processing."""
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._message_processor_task = asyncio.create_task(self._process_messages())

    async def _handle_messages(self) -> None:
        """Handle incoming WebSocket messages."""
        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self._message_queue.put(json.loads(msg.data))
                elif msg.type in (
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.ERROR,
                ):
                    await self._reconnect()
                    break
        except Exception:
            await self._reconnect()

    async def _process_messages(self) -> None:
        """Process messages from the message queue."""
        while True:
            try:
                message = await self._message_queue.get()
                await asyncio.to_thread(self._message_handler, message)
                self._message_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception:
                continue

    async def _health_check_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(self._config["health_check_interval"])
                if not self._is_connected or not self._ws or self._ws.closed:
                    await self._reconnect()
                else:
                    await self._ping_listen_key()
            except asyncio.CancelledError:
                break
            except Exception:
                if not self._fatal_error:  # Only try reconnect if not fatally failed
                    await self._reconnect()
                else:
                    break  # Exit loop if we've had a fatal error

    async def _ping_listen_key(self) -> None:
        """Keep the listen key alive by pinging Binance."""
        try:
            ws = await self._session.ws_connect("wss://ws-fapi.binance.com/ws-fapi/v1")
            await ws.send_json(
                {
                    "id": self._get_next_id(),
                    "method": "userDataStream.ping",
                    "params": {
                        "listenKey": self._listen_key,
                        "apiKey": self._api_key,
                    },
                }
            )

            response = await ws.receive_json(timeout=self._config["request_timeout"])
            await ws.close()

            if response.get("status") != 200:
                raise UserStreamError("Listen key ping failed")
        except Exception:
            await self._reconnect()

    async def _cleanup(self) -> None:
        """Clean up all resources and reset state."""
        self._is_connected = False

        for task in [self._health_check_task, self._message_processor_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        if self._ws:
            await self._ws.close()

        if self._session and not self._session.closed:
            await self._session.close()

        self._ws = None
        self._session = None
        self._listen_key = None

        while not self._message_queue.empty():
            try:
                self._message_queue.get_nowait()
                self._message_queue.task_done()
            except asyncio.QueueEmpty:
                break

    async def _reconnect(self) -> None:
        """Handle reconnection with exponential backoff."""
        async with self._connection_lock:
            if self._fatal_error:
                return  # Don't attempt reconnect if we've had a fatal error

            await self._cleanup()
            retry_count = 0
            delay = self._config["reconnect_delay"]

            while retry_count < self._config["max_reconnect_attempts"]:
                try:
                    await self._initialize_listen_key()
                    await self._establish_connection()
                    self._start_background_tasks()
                    self._is_connected = True
                    return
                except Exception:
                    retry_count += 1
                    if retry_count < self._config["max_reconnect_attempts"]:
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, self._config["max_reconnect_delay"])

            # Mark as fatally failed before cleanup and raise
            self._fatal_error = True
            await self._cleanup()
            raise ConnectionError("Failed to reconnect after maximum retries")

    def _get_next_id(self) -> int:
        """Generate a unique message ID."""
        self._message_id += 1
        return self._message_id
