from datetime import datetime
from typing import Any, Dict, Optional

from .base import AbstractPercentage


class LinearRampPercentage(AbstractPercentage):
    def __init__(
        self,
        initial_value: float = 0.0,
        final_value: float = 1.0,
        ramp_duration: int = 3600,
        initial_time: Optional[int] = None,
    ):
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
    def from_dict(cls, fields: Dict[str, Any]) -> "Percentage":
        return cls(
            initial_value=fields.get("initial_value"),
            final_value=fields.get("final_value"),
            ramp_duration=fields.get("ramp_duration"),
            initial_time=fields.get("initial_time"),
        )
