from typing import Any, Iterable

from .interface import AbstractOperator


class NegatedSetMembershipOperator(AbstractOperator):
    SYMBOL = "not_in"

    def compare(self, expected: Iterable, actual: Any) -> bool:
        return expected not in actual
