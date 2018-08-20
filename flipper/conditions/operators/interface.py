from abc import ABCMeta, abstractmethod
from typing import Any


class AbstractOperator(metaclass=ABCMeta):
    @property
    @abstractmethod
    def SYMBOL(self) -> str:
        pass

    @abstractmethod
    def compare(self, expected: Any, actual: Any) -> bool:
        pass
