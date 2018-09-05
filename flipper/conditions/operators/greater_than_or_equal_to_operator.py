from typing import Any

from .interface import AbstractOperator


class GreaterThanOrEqualToOperator(AbstractOperator):
    SYMBOL = "gte"

    def compare(self, expected: Any, actual: Any) -> bool:
        return expected >= actual
