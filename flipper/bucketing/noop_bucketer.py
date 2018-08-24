from typing import Any, Dict

from .base import AbstractBucketer


class NoOpBucketer(AbstractBucketer):
    @classmethod
    def get_type(cls) -> str:
        return 'NoOpBucketer'

    def check(self, **checks) -> bool:
        return True

    def toJSON(self) -> Dict[str, Any]:
        return super().toJSON()

    @classmethod
    def fromJSON(
        cls,
        fields: Dict[str, Any],
    ) -> 'PercentageBucketer':
        return cls()
