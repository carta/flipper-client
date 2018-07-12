from abc import ABCMeta, abstractmethod
from typing import Optional

from .storage import FeatureFlagStoreItem


class AbstractFeatureFlagStore(metaclass=ABCMeta):
    @abstractmethod
    def create(
        self,
        feature_name: str,
        is_enabled: Optional[bool] = False,
        metadata: Optional[dict] = None,
    ):
        pass

    @abstractmethod
    def get(self, feature_name: str) -> FeatureFlagStoreItem:
        pass

    @abstractmethod
    def set(
        self,
        feature_name: str,
        is_enabled: bool,
        metadata: Optional[dict] = None,
    ):
        pass

    @abstractmethod
    def delete(self, feature_name: str):
        pass
