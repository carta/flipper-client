from typing import Any

from .interface import AbstractOperator


class NegationOperator(AbstractOperator):
    SYMBOL = 'ne'

    def compare(self, expected: Any, actual: Any) -> bool:
        return expected != actual
