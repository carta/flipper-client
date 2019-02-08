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

from datetime import datetime
from typing import Any, Dict, Optional, cast

from .base import AbstractPercentage


class LinearRampPercentage(AbstractPercentage):
    def __init__(
        self,
        initial_value: float = 0.0,
        final_value: float = 1.0,
        ramp_duration: int = 3600,
        initial_time: Optional[int] = None,
    ) -> None:
        self._initial_value = initial_value
        self._final_value = final_value
        self._ramp_duration = ramp_duration
        if initial_time is None:
            self._initial_time = datetime.now()
        else:
            self._initial_time = datetime.fromtimestamp(initial_time)

    @classmethod
    def get_type(cls) -> str:
        return "LinearRampPercentage"

    @property
    def value(self) -> float:
        if self._ramp_duration == 0:
            return self._final_value
        return min(self._final_value, self.slope * self.dt + self._initial_value)

    @property
    def slope(self) -> float:
        return (self._final_value - self._initial_value) / self._ramp_duration

    @property
    def dt(self) -> int:
        return (datetime.now() - self._initial_time).seconds

    def to_dict(self) -> Dict[str, Any]:
        return {
            **super().to_dict(),
            "initial_value": self._initial_value,
            "final_value": self._final_value,
            "ramp_duration": self._ramp_duration,
            "initial_time": int(self._initial_time.timestamp()),
        }

    @classmethod
    def from_dict(cls, fields: Dict[str, Any]) -> "LinearRampPercentage":
        return cls(
            initial_value=cast(float, fields.get("initial_value", 0.0)),
            final_value=cast(float, fields.get("final_value", 1.0)),
            ramp_duration=cast(int, fields.get("ramp_duration", 3600)),
            initial_time=fields.get("initial_time"),
        )
