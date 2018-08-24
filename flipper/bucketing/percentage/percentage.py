from typing import Any, Dict

from .base import AbstractPercentage


class Percentage(AbstractPercentage):
    def __init__(self, value: float=1.0):
        self._value = value

    @classmethod
    def get_type(cls) -> str:
        return 'Percentage'

    @property
    def value(self):
        return self._value

    def toJSON(self) -> Dict[str, Any]:
        return {
            **super().toJSON(),
            'value': self._value
        }

    @classmethod
    def fromJSON(cls, fields: Dict[str, Any]) -> 'Percentage':
        return cls(value=fields.get('value'))
