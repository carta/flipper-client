from abc import ABCMeta, abstractmethod
from typing import Optional

from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta


class AbstractFeatureFlagStore(metaclass=ABCMeta):
    @abstractmethod
    def create(
        self,
        feature_name: str,
        is_enabled: Optional[bool] = False,
        client_data: Optional[dict] = None,
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
    ):
        pass

    @abstractmethod
    def delete(self, feature_name: str):
        pass

    @abstractmethod
    def set_meta(self, feature_name: str, meta: FeatureFlagStoreMeta):
        pass


class FlagDoesNotExistError(Exception):
    pass
