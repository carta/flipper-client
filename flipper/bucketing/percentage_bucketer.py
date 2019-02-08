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

import random
from typing import Any, Dict

from .base import AbstractBucketer
from .percentage import AbstractPercentage, Percentage, PercentageFactory


class PercentageBucketer(AbstractBucketer):
    def __init__(self, percentage: AbstractPercentage = None) -> None:
        self._percentage = percentage or Percentage()

    @classmethod
    def get_type(cls) -> str:
        return "PercentageBucketer"

    @property
    def percentage(self):
        return self._percentage.value

    def check(self, randomizer=random.random, **checks) -> bool:
        if self._percentage == 0.0:
            return False
        return randomizer() <= self._percentage

    def to_dict(self) -> Dict[str, Any]:
        return {**super().to_dict(), "percentage": self._percentage.to_dict()}

    @classmethod
    def from_dict(cls, fields: Dict[str, Any]) -> "PercentageBucketer":
        percentage = None
        percentage_fields = fields.get("percentage")
        if percentage_fields is not None:
            percentage = PercentageFactory.create(percentage_fields)
        return cls(percentage=percentage)
