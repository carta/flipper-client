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
