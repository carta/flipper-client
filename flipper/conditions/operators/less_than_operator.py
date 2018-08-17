from typing import Any

from .interface import AbstractOperator


class LessThanOperator(AbstractOperator):
    SYMBOL = 'lt'

    def compare(self, expected: Any, actual: Any) -> bool:
        return expected < actual
