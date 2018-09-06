from typing import Any, Dict, Type, Union

from .base import AbstractPercentage
from .linear_ramp_percentage import LinearRampPercentage
from .percentage import Percentage

PercentageTypes = Union[Type[LinearRampPercentage], Type[Percentage]]


class PercentageFactory:
    PERCENTAGE_MAP = {
        LinearRampPercentage.get_type(): LinearRampPercentage,
        Percentage.get_type(): Percentage,
    }  # type: Dict[str, PercentageTypes]

    class InvalidPercentageTypeError(Exception):
        pass

    @classmethod
    def create(cls, fields: Dict[str, Any]) -> AbstractPercentage:
        try:
            return cls.PERCENTAGE_MAP[fields["type"]].from_dict(fields)
        except KeyError:
            raise cls.InvalidPercentageTypeError(
                "Percentage type not supported: %s" % fields["type"]
            )
