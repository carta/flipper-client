from abc import ABCMeta, abstractmethod
from typing import Optional

from .storage import FeatureFlagStoreItem


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

    def set_client_data(
        self,
        feature_name: str,
        client_data: dict,
    ):
        pass


class FlagDoesNotExistError(Exception):
    pass
