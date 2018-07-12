from datetime import datetime
from typing import Optional

from .interface import AbstractFeatureFlagStore
from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta
from .util.date import now


class MemoryFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self):
        self._memory = {}

    def create(
        self,
        feature_name: str,
        is_enabled: Optional[bool] = False,
        client_data: Optional[dict] = None,
    ) -> FeatureFlagStoreItem:
        self.set(feature_name, is_enabled, client_data=client_data)
        return self.get(feature_name)

    def get(self, feature_name: str) -> FeatureFlagStoreItem:
        return self._memory.get(feature_name)

    def set(
        self,
        feature_name: str,
        is_enabled: bool,
        client_data: Optional[dict] = None,
    ):
        client_data = client_data or {}

        flag = FeatureFlagStoreItem(
            feature_name,
            is_enabled,
            FeatureFlagStoreMeta(now(), client_data),
        )
        self._memory[feature_name] = flag

    def delete(self, feature_name: str):
        if feature_name in self._memory:
            del self._memory[feature_name]
