import hashlib
import hmac
from typing import (
    Any,
    Dict,
)

from .base import BaseAuth


class HMACAuth(BaseAuth):
    def __init__(self, api_key: str, secret_key: str):
        super().__init__(api_key)
        self.secret_key = secret_key

    async def sign(self, params: Dict[str, Any]) -> str:
        # Convert boolean values to lowercase strings for signature generation
        signature_params = {
            k: str(v).lower() if isinstance(v, bool) else v for k, v in params.items()
        }

        payload = "&".join(
            [
                f"{param}={value}"
                for param, value in sorted(signature_params.items())
                if param != "signature"
            ]
        )

        signature = hmac.new(
            self.secret_key.encode("ASCII"),
            payload.encode("ASCII"),
            hashlib.sha256,
        ).hexdigest()

        return signature
