import base64
from typing import (
    Any,
    Dict,
)

from cryptography.hazmat.primitives.serialization import load_pem_private_key

from .base import BaseAuth


class Ed25519Auth(BaseAuth):
    def __init__(self, api_key: str, private_key_path: str):
        super().__init__(api_key)
        self.private_key = self._load_private_key(private_key_path)

    def _load_private_key(self, private_key_path: str):
        with open(private_key_path, "rb") as f:
            return load_pem_private_key(data=f.read(), password=None)

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
        signature = self.private_key.sign(payload.encode("ASCII"))
        return base64.b64encode(signature).decode("ASCII")
