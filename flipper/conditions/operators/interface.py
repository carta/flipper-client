from abc import ABCMeta, abstractmethod
from typing import Any, Optional


class AbstractOperator(metaclass=ABCMeta):
    @property
    @abstractmethod
    def SYMBOL(self) -> Optional[str]:
        pass

    @abstractmethod
    def compare(self, expected: Any, actual: Any) -> bool:
        pass
