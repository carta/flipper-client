from abc import ABCMeta, abstractmethod
from typing import Any, Dict


class AbstractPercentage(metaclass=ABCMeta):
    @property
    @abstractmethod
    def value(self, **checks) -> float:
        pass

    @classmethod
    @abstractmethod
    def get_type(cls) -> str:
        pass

    @abstractmethod
    def toJSON(self) -> Dict[str, Any]:
        return { 'type': self.get_type() }

    @classmethod
    @abstractmethod
    def fromJSON(cls, fields: Dict[str, Any]) -> 'AbstractPercentage':
        pass

    def __gt__(self, comparison: float) -> bool:
        return self.value > comparison

    def __ge__(self, comparison: float) -> bool:
        return self.value >= comparison

    def __lt__(self, comparison: float) -> bool:
        return self.value < comparison

    def __le__(self, comparison: float) -> bool:
        return self.value <= comparison

    def __eq__(self, comparison: float) -> bool:
        return self.value == comparison
