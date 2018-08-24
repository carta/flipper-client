from typing import Any, Dict

from .base import AbstractPercentage
from .linear_ramp_percentage import LinearRampPercentage
from .percentage import Percentage


class PercentageFactory:
    PERCENTAGE_MAP = {
        LinearRampPercentage.get_type(): LinearRampPercentage,
        Percentage.get_type(): Percentage,
    }

    class InvalidPercentageTypeError(Exception):
        pass

    @classmethod
    def create(cls, fields: Dict[str, Any]) -> AbstractPercentage:
        try:
            return cls.PERCENTAGE_MAP[fields['type']].fromJSON(fields)
        except KeyError:
            raise cls.InvalidPercentageTypeError(
                'Percentage type not supported: %s' % fields['type']
            )
