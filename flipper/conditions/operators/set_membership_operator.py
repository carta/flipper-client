from typing import Any, Iterable

from .interface import AbstractOperator


class SetMembershipOperator(AbstractOperator):
    SYMBOL = 'in'

    def compare(self, expected: Iterable, actual: Any) -> bool:
        return expected in actual
