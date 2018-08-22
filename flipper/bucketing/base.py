from abc import ABCMeta, abstractmethod
from typing import Any, Dict


class AbstractBucketer(metaclass=ABCMeta):
    @abstractmethod
    def check(self, **checks) -> bool:
        pass

    @classmethod
    @abstractmethod
    def get_type(cls) -> str:
        pass

    @abstractmethod
    def toJSON(self) -> Dict[str, Any]:
        pass

    @classmethod
    @abstractmethod
    def fromJSON(cls, fields: Dict[str, Any]) -> 'AbstractBucketer':
        pass
