from typing import Any

from .interface import AbstractOperator


class LessThanOrEqualToOperator(AbstractOperator):
    SYMBOL = "lte"

    def compare(self, expected: Any, actual: Any) -> bool:
        return expected <= actual
