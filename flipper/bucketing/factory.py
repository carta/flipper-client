# Copyright 2018 eShares, Inc. dba Carta, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from typing import Any, Dict

from .base import AbstractBucketer
from .consistent_hash_percentage_bucketer import ConsistentHashPercentageBucketer
from .noop_bucketer import NoOpBucketer
from .percentage_bucketer import PercentageBucketer


class BucketerFactory:
    BUCKETER_MAP = {
        ConsistentHashPercentageBucketer.get_type(): ConsistentHashPercentageBucketer,
        NoOpBucketer.get_type(): NoOpBucketer,
        PercentageBucketer.get_type(): PercentageBucketer,
    }

    class InvalidBucketerTypeError(Exception):
        pass

    @classmethod
    def create(cls, fields: Dict[str, Any]) -> AbstractBucketer:
        try:
            return cls.BUCKETER_MAP[fields["type"]].from_dict(fields)  # type: ignore
        except KeyError:
            raise cls.InvalidBucketerTypeError(
                "Bucketer type not supported: %s" % fields["type"]
            )
