from typing import Any

from .interface import AbstractOperator


class EqualityOperator(AbstractOperator):
    SYMBOL = None

    def compare(self, expected: Any, actual: Any) -> bool:
        return expected == actual
