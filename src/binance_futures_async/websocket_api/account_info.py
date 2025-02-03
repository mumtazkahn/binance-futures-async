# src/position_info.py

from typing import (
    Any,
    Dict,
    List,
)


class AccountInfo:

    def get_position_info(self, symbol: str = None) -> List[Dict[str, Any]]:
        params = {}
        if symbol:
            params["symbol"] = symbol
        return params

    def get_account_balance(self) -> Dict[str, Any]:
        return {}

    def get_account_status(self) -> Dict[str, Any]:
        return {}
