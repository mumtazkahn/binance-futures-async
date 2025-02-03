from decimal import (
    Decimal,
    DecimalException,
)
from enum import Enum
from typing import (
    Any,
    Dict,
)

from ..exceptions import OrderValidationError


class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"
    STOP_MARKET = "STOP_MARKET"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_MARKET = "TAKE_PROFIT_MARKET"
    TRAILING_STOP_MARKET = "TRAILING_STOP_MARKET"


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class PositionSide(Enum):
    BOTH = "BOTH"
    LONG = "LONG"
    SHORT = "SHORT"


class TimeInForce(Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"
    GTX = "GTX"
    GTD = "GTD"


class WorkingType(Enum):
    MARK_PRICE = "MARK_PRICE"
    CONTRACT_PRICE = "CONTRACT_PRICE"


class NewOrderRespType(Enum):
    ACK = "ACK"
    RESULT = "RESULT"


class SelfTradePreventionMode(Enum):
    NONE = "NONE"
    EXPIRE_TAKER = "EXPIRE_TAKER"
    EXPIRE_MAKER = "EXPIRE_MAKER"
    EXPIRE_BOTH = "EXPIRE_BOTH"


class PriceMatch(Enum):
    NONE = "NONE"
    OPPONENT = "OPPONENT"
    OPPONENT_5 = "OPPONENT_5"
    OPPONENT_10 = "OPPONENT_10"
    OPPONENT_20 = "OPPONENT_20"
    QUEUE = "QUEUE"
    QUEUE_5 = "QUEUE_5"
    QUEUE_10 = "QUEUE_10"
    QUEUE_20 = "QUEUE_20"


class OrderPreparation:
    def __init__(self, enable_validation):
        self.enable_validation = enable_validation

    def _validate_decimal(self, value: Any, param_name: str) -> Decimal:
        try:
            return Decimal(str(value))
        except (ValueError, TypeError, DecimalException):
            raise OrderValidationError(f"{param_name} must be a valid number")

    def _validate_enum(self, value: Any, enum_class: type, param_name: str) -> Enum:
        try:
            return enum_class(value)
        except ValueError:
            valid_values = ", ".join([e.value for e in enum_class])
            raise OrderValidationError(f"{param_name} must be one of: {valid_values}")

    def _validate_boolean(self, value: Any, param_name: str) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
        raise OrderValidationError(f"{param_name} must be a boolean value")

    def _validate_common_params(self, kwargs: Dict[str, Any], params: Dict[str, Any]):
        if "symbol" not in kwargs:
            raise OrderValidationError("symbol is required")
        params["symbol"] = kwargs["symbol"]

        if "side" not in kwargs:
            raise OrderValidationError("side is required")
        params["side"] = self._validate_enum(kwargs["side"], OrderSide, "side").value

        optional_params = [
            "positionSide",
            "newClientOrderId",
            "reduceOnly",
            "newOrderRespType",
            "priceMatch",
            "selfTradePreventionMode",
            "recvWindow",
            "priceProtect",
            "workingType",
            "activationPrice",
            "callbackRate",
            "closePosition",
            "goodTillDate",
        ]

        for param in optional_params:
            if param in kwargs:
                if param == "positionSide":
                    params[param] = self._validate_enum(
                        kwargs[param], PositionSide, param
                    ).value
                elif param == "newOrderRespType":
                    params[param] = self._validate_enum(
                        kwargs[param], NewOrderRespType, param
                    ).value
                elif param == "selfTradePreventionMode":
                    params[param] = self._validate_enum(
                        kwargs[param], SelfTradePreventionMode, param
                    ).value
                elif param == "priceMatch":
                    params[param] = self._validate_enum(
                        kwargs[param], PriceMatch, param
                    ).value
                elif param == "workingType":
                    params[param] = self._validate_enum(
                        kwargs[param], WorkingType, param
                    ).value
                elif param in ["reduceOnly", "priceProtect", "closePosition"]:
                    params[param] = self._validate_boolean(kwargs[param], param)
                elif param in ["activationPrice", "callbackRate"]:
                    params[param] = self._validate_decimal(kwargs[param], param)
                elif param == "recvWindow":
                    if not isinstance(kwargs[param], int) or kwargs[param] <= 0:
                        raise OrderValidationError(
                            "recvWindow must be a positive integer"
                        )
                    params[param] = kwargs[param]
                else:
                    params[param] = kwargs[param]

    def place_limit_order(self, **kwargs) -> Dict[str, Any]:
        params = {"type": OrderType.LIMIT.value}

        if self.enable_validation:
            self._validate_common_params(kwargs, params)

            if "timeInForce" not in kwargs:
                raise OrderValidationError("timeInForce is required for LIMIT orders")
            params["timeInForce"] = self._validate_enum(
                kwargs["timeInForce"], TimeInForce, "timeInForce"
            ).value

            if "quantity" not in kwargs:
                raise OrderValidationError("quantity is required for LIMIT orders")
            params["quantity"] = self._validate_decimal(kwargs["quantity"], "quantity")

            if "price" not in kwargs and "priceMatch" not in kwargs:
                raise OrderValidationError(
                    "Either price or priceMatch is required for LIMIT orders"
                )

            if "price" in kwargs:
                params["price"] = self._validate_decimal(kwargs["price"], "price")

            if "goodTillDate" in kwargs:
                if params["timeInForce"] != TimeInForce.GTD.value:
                    raise OrderValidationError(
                        "goodTillDate can only be used with timeInForce GTD"
                    )
                params["goodTillDate"] = kwargs["goodTillDate"]
        else:
            params.update(kwargs)

        return params

    def place_market_order(self, **kwargs) -> Dict[str, Any]:
        params = {"type": OrderType.MARKET.value}

        if self.enable_validation:
            self._validate_common_params(kwargs, params)

            if "quantity" not in kwargs:
                raise OrderValidationError("quantity is required for MARKET orders")
            params["quantity"] = self._validate_decimal(kwargs["quantity"], "quantity")
        else:
            params.update(kwargs)

        return params

    def place_stop_order(self, **kwargs) -> Dict[str, Any]:
        params = {"type": OrderType.STOP.value}

        if self.enable_validation:
            self._validate_common_params(kwargs, params)

            if "quantity" not in kwargs:
                raise OrderValidationError("quantity is required for STOP orders")
            params["quantity"] = self._validate_decimal(kwargs["quantity"], "quantity")

            if "price" not in kwargs and "priceMatch" not in kwargs:
                raise OrderValidationError(
                    "Either price or priceMatch is required for STOP orders"
                )

            if "price" in kwargs:
                params["price"] = self._validate_decimal(kwargs["price"], "price")

            if "stopPrice" not in kwargs:
                raise OrderValidationError("stopPrice is required for STOP orders")
            params["stopPrice"] = self._validate_decimal(
                kwargs["stopPrice"], "stopPrice"
            )

            if "timeInForce" in kwargs:
                params["timeInForce"] = self._validate_enum(
                    kwargs["timeInForce"], TimeInForce, "timeInForce"
                ).value
        else:
            params.update(kwargs)

        return params

    def place_stop_market_order(self, **kwargs) -> Dict[str, Any]:
        params = {"type": OrderType.STOP_MARKET.value}

        if self.enable_validation:
            self._validate_common_params(kwargs, params)

            if "stopPrice" not in kwargs:
                raise OrderValidationError(
                    "stopPrice is required for STOP_MARKET orders"
                )
            params["stopPrice"] = self._validate_decimal(
                kwargs["stopPrice"], "stopPrice"
            )

            if "closePosition" in kwargs:
                params["closePosition"] = self._validate_boolean(
                    kwargs["closePosition"], "closePosition"
                )
                if params["closePosition"] and "quantity" in kwargs:
                    raise OrderValidationError(
                        "quantity cannot be sent with closePosition=true"
                    )
            elif "quantity" not in kwargs:
                raise OrderValidationError(
                    "quantity is required for STOP_MARKET orders when closePosition is not true"
                )
            else:
                params["quantity"] = self._validate_decimal(
                    kwargs["quantity"], "quantity"
                )
        else:
            params.update(kwargs)

        return params

    def place_take_profit_order(self, **kwargs) -> Dict[str, Any]:
        params = {"type": OrderType.TAKE_PROFIT.value}

        if self.enable_validation:
            self._validate_common_params(kwargs, params)

            if "quantity" not in kwargs:
                raise OrderValidationError(
                    "quantity is required for TAKE_PROFIT orders"
                )
            params["quantity"] = self._validate_decimal(kwargs["quantity"], "quantity")

            if "price" not in kwargs and "priceMatch" not in kwargs:
                raise OrderValidationError(
                    "Either price or priceMatch is required for TAKE_PROFIT orders"
                )

            if "price" in kwargs:
                params["price"] = self._validate_decimal(kwargs["price"], "price")

            if "stopPrice" not in kwargs:
                raise OrderValidationError(
                    "stopPrice is required for TAKE_PROFIT orders"
                )
            params["stopPrice"] = self._validate_decimal(
                kwargs["stopPrice"], "stopPrice"
            )

            if "timeInForce" in kwargs:
                params["timeInForce"] = self._validate_enum(
                    kwargs["timeInForce"], TimeInForce, "timeInForce"
                ).value
        else:
            params.update(kwargs)

        return params

    def place_take_profit_market_order(self, **kwargs) -> Dict[str, Any]:
        params = {"type": OrderType.TAKE_PROFIT_MARKET.value}

        if self.enable_validation:
            self._validate_common_params(kwargs, params)

            if "stopPrice" not in kwargs:
                raise OrderValidationError(
                    "stopPrice is required for TAKE_PROFIT_MARKET orders"
                )
            params["stopPrice"] = self._validate_decimal(
                kwargs["stopPrice"], "stopPrice"
            )

            if "closePosition" in kwargs:
                params["closePosition"] = self._validate_boolean(
                    kwargs["closePosition"], "closePosition"
                )
                if params["closePosition"] and "quantity" in kwargs:
                    raise OrderValidationError(
                        "quantity cannot be sent with closePosition=true"
                    )
            elif "quantity" not in kwargs:
                raise OrderValidationError(
                    "quantity is required for TAKE_PROFIT_MARKET orders when closePosition is not true"
                )
            else:
                params["quantity"] = self._validate_decimal(
                    kwargs["quantity"], "quantity"
                )
        else:
            params.update(kwargs)

        return params

    def place_trailing_stop_market_order(self, **kwargs) -> Dict[str, Any]:
        params = {"type": OrderType.TRAILING_STOP_MARKET.value}

        if self.enable_validation:
            self._validate_common_params(kwargs, params)

            if "callbackRate" not in kwargs:
                raise OrderValidationError(
                    "callbackRate is required for TRAILING_STOP_MARKET orders"
                )
            params["callbackRate"] = self._validate_decimal(
                kwargs["callbackRate"], "callbackRate"
            )

            if "quantity" not in kwargs:
                raise OrderValidationError(
                    "quantity is required for TRAILING_STOP_MARKET orders"
                )
            params["quantity"] = self._validate_decimal(kwargs["quantity"], "quantity")

            if "activationPrice" in kwargs:
                params["activationPrice"] = self._validate_decimal(
                    kwargs["activationPrice"], "activationPrice"
                )
        else:
            params.update(kwargs)

        return params
