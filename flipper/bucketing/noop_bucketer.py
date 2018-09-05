from typing import Any, Dict

from .base import AbstractBucketer


class NoOpBucketer(AbstractBucketer):
    @classmethod
    def get_type(cls) -> str:
        return "NoOpBucketer"

    def check(self, **checks) -> bool:
        return True

    def to_dict(self) -> Dict[str, Any]:
        return super().to_dict()

    @classmethod
    def from_dict(cls, fields: Dict[str, Any]) -> "NoOpBucketer":
        return cls()
