from typing import Any, Dict

from .base import AbstractBucketer
from .consistent_hash_percentage_bucketer import ConsistentHashPercentageBucketer
from .noop_bucketer import NoOpBucketer
from .percentage_bucketer import PercentageBucketer


class BucketerFactory:
    BUCKETER_MAP = {
        ConsistentHashPercentageBucketer.get_type(): ConsistentHashPercentageBucketer,  # noqa: E501
        NoOpBucketer.get_type(): NoOpBucketer,
        PercentageBucketer.get_type(): PercentageBucketer,
    }

    class InvalidBucketerTypeError(Exception):
        pass

    @classmethod
    def create(cls, fields: Dict[str, Any]) -> AbstractBucketer:
        try:
            return cls.BUCKETER_MAP[fields["type"]].from_dict(fields)
        except KeyError:
            raise cls.InvalidBucketerTypeError(
                "Bucketer type not supported: %s" % fields["type"]
            )
