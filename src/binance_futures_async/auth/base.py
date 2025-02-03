from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Any,
    Dict,
)


class BaseAuth(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    async def sign(self, params: Dict[str, Any]) -> str:
        pass
