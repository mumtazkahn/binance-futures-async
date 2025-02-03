# exceptions.py
class BinanceWebSocketError(Exception):
    """Base exception for BinanceWebSocketClient errors."""


class ConnectionError(Exception):
    """Raised when a connection error occurs."""


class AuthenticationError(Exception):
    """Raised when authentication fails."""


class RequestError(Exception):
    """Raised when a request fails."""


class UserStreamError(Exception):
    """Exception raised for errors specific to the UserDataStream."""


class OrderValidationError(Exception):
    """Raised when order validation fails."""
