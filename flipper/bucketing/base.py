from abc import ABCMeta, abstractmethod
from typing import Any, Dict


class AbstractBucketer(metaclass=ABCMeta):
    @abstractmethod
    def check(self, **checks) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def get_type() -> str:
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.get_type()}

    @classmethod
    @abstractmethod
    def from_dict(cls, fields: Dict[str, Any]) -> "AbstractBucketer":
        pass
