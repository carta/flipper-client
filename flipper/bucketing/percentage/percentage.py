from typing import Any, Dict, Optional

from .base import AbstractPercentage


class Percentage(AbstractPercentage):
    def __init__(self, value: Optional[float] = 1.0) -> None:
        self._value = value

    @classmethod
    def get_type(cls) -> str:
        return "Percentage"

    @property
    def value(self):
        return self._value

    def to_dict(self) -> Dict[str, Any]:
        return {**super().to_dict(), "value": self._value}

    @classmethod
    def from_dict(cls, fields: Dict[str, Any]) -> "Percentage":
        return cls(value=fields.get("value"))
