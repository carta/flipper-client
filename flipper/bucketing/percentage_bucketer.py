import random
from typing import Any, Dict

from .base import AbstractBucketer
from .percentage import AbstractPercentage, Percentage, PercentageFactory


class PercentageBucketer(AbstractBucketer):
    def __init__(self, percentage: AbstractPercentage=None):
        self._percentage = percentage or Percentage()

    @classmethod
    def get_type(cls) -> str:
        return 'PercentageBucketer'

    @property
    def percentage(self):
        return self._percentage.value

    def check(self, randomizer=random.random, **checks) -> bool:
        if self._percentage == 0.0:
            return False
        return randomizer() <= self._percentage

    def toJSON(self) -> Dict[str, Any]:
        return {
            'type': PercentageBucketer.get_type(),
            'percentage': self._percentage.toJSON(),
        }

    @classmethod
    def fromJSON(
        cls,
        fields: Dict[str, Any],
    ) -> 'PercentageBucketer':
        percentage = None
        percentage_fields = fields.get('percentage')
        if percentage_fields is not None:
            percentage = PercentageFactory.create(percentage_fields)
        return cls(percentage=percentage)
