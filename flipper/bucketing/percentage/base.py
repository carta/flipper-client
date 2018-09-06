import numbers
from abc import ABCMeta, abstractmethod
from typing import Any, Dict


class AbstractPercentage(metaclass=ABCMeta):
    @property
    @abstractmethod
    def value(self) -> float:
        pass

    @staticmethod
    @abstractmethod
    def get_type() -> str:
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.get_type()}

    @classmethod
    @abstractmethod
    def from_dict(cls, fields: Dict[str, Any]) -> "AbstractPercentage":
        pass

    def __gt__(self, comparison) -> bool:
        self._assert_is_valid_comparison_type(comparison)
        return self.value > comparison

    def _assert_is_valid_comparison_type(self, comparison) -> None:
        assert isinstance(comparison, numbers.Number)

    def __ge__(self, comparison) -> bool:
        self._assert_is_valid_comparison_type(comparison)
        return self.value >= comparison

    def __lt__(self, comparison) -> bool:
        self._assert_is_valid_comparison_type(comparison)
        return self.value < comparison

    def __le__(self, comparison) -> bool:
        self._assert_is_valid_comparison_type(comparison)
        return self.value <= comparison

    def __eq__(self, comparison) -> bool:
        self._assert_is_valid_comparison_type(comparison)
        return self.value == comparison
