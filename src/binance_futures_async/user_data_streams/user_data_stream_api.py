from typing import (
    Any,
    Callable,
    Dict,
    Optional,
)

from .user_data_stream_infrastructure import UserDataStreamInfrastructure


class UserDataStreamAPI:
    """
    API for managing user data streams from Binance.
    Handles user account updates, balance changes, and order updates.
    """

    def __init__(
        self,
        api_key: str,
        message_handler: Callable[[Dict[str, Any]], None],
        config: Dict[str, Any],
    ):
        """
        Initialize the user data stream API.

        Args:
            api_key: The Binance API key
            message_handler: Callback function to handle incoming messages
            config: Configuration dictionary for stream behavior
        """
        if not callable(message_handler):
            raise ValueError("message_handler must be a callable")

        self._infrastructure = UserDataStreamInfrastructure(
            api_key=api_key, message_handler=message_handler, config=config
        )

    async def start(self) -> None:
        """
        Start the user data stream connection.
        Raises ConnectionError if the connection cannot be established.
        """
        await self._infrastructure.start()

    async def stop(self) -> None:
        """
        Stop the user data stream connection and cleanup resources.
        """
        await self._infrastructure.stop()

    @property
    def is_connected(self) -> bool:
        """
        Check if the stream is currently connected.
        Returns: bool indicating connection status
        """
        return self._infrastructure.is_connected

    @property
    def listen_key(self) -> Optional[str]:
        """
        Get the current listen key for the stream.
        Returns: Current listen key or None if not connected
        """
        return self._infrastructure.listen_key
