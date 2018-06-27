from abc import ABCMeta, abstractmethod
from typing import Optional


class AbstractFeatureFlagStore(metaclass=ABCMeta):
    @abstractmethod
    def create(self, feature_name: str, is_enabled: Optional[bool]=False):
        pass

    @abstractmethod
    def get(self, feature_name: str, default: Optional[bool]=False) -> bool:
        pass

    @abstractmethod
    def set(self, feature_name: str, is_enabled: bool):
        pass

    @abstractmethod
    def delete(self, feature_name: str):
        pass
