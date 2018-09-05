from typing import Any

from .interface import AbstractOperator


class GreaterThanOperator(AbstractOperator):
    SYMBOL = "gt"

    def compare(self, expected: Any, actual: Any) -> bool:
        return expected > actual
